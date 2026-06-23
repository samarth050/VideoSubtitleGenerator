import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
from services.transcription import Transcriber
from services.subtitle_writer import save_srt
from services.video_validator import VideoValidator


class MainWindow:

    def __init__(self, root):

        self.root = root

        root.title("Video Subtitle Generator")

        root.geometry("1000x700")

        self.transcriber = None

        self.video_path = tk.StringVar()

        # -------------------------
        # Video File
        # -------------------------

        tk.Label(
            root,
            text="Video File"
        ).pack(pady=5)

        tk.Entry(
            root,
            textvariable=self.video_path,
            width=100
        ).pack()

        tk.Button(
            root,
            text="Browse",
            command=self.browse
        ).pack(pady=5)

        self.file_label = tk.Label(
            root,
            text="No file selected"
        )

        self.file_label.pack()
        # -------------------------
        # Generate Button
        # -------------------------

        self.generate_btn = tk.Button(
            root,
            text="Generate English Subtitles",
            command=self.start_transcription
        )

        self.generate_btn.pack(pady=10)

        # -------------------------
        # Status
        # -------------------------

        self.status_label = tk.Label(
            root,
            text="Ready"
        )

        self.status_label.pack()


        # -------------------------
        # Validation Message
        # -------------------------

        self.validation_label = tk.Label(
            root,
            text="",
            wraplength=900,
            justify="left"
        )

        self.validation_label.pack()

        # -------------------------
        # Language
        # -------------------------

        self.language_label = tk.Label(
            root,
            text="Detected Language: Unknown"
        )

        self.language_label.pack(pady=5)

        # -------------------------
        # Transcript Preview
        # -------------------------

        self.preview = ScrolledText(
            root,
            width=120,
            height=30
        )

        self.preview.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ----------------------------------
    # Browse
    # ----------------------------------
    def start_transcription(self):

        if not self.video_path.get():

            messagebox.showerror(
                "Error",
                "Please select a video file."
            )

            return

        self.preview.delete(
            "1.0",
            tk.END
        )

        self.generate_btn.config(
            state="disabled"
        )

        thread = threading.Thread(
            target=self.transcribe_video,
            daemon=True
        )

        thread.start()

    def browse(self):

        file = filedialog.askopenfilename(
            filetypes=[
                (
                    "Video Files",
                    "*.mp4 *.mkv *.avi *.mov *.wmv"
                )
            ]
        )

        if file:

            self.video_path.set(file)

            self.file_label.config(
                text=file
            )

    # ----------------------------------
    # Actual Processing
    # ----------------------------------

    def transcribe_video(self):

        try:

            self.update_status(
                "Validating Video..."
            )

            valid, message = (
                VideoValidator.validate(
                    self.video_path.get()
                )
            )

            duration = (
                VideoValidator.get_duration(
                    self.video_path.get()
                )
            )

            size_gb = (
                os.path.getsize(
                    self.video_path.get()
                )
                / (1024 ** 3)
            )

            low, high = (
                VideoValidator.estimate_processing_time(
                    duration,
                    "base"
                )
            )

            validation_text = (
                f"{message}\n"
                f"File Size: {size_gb:.2f} GB\n"
                f"Duration: "
                f"{VideoValidator.format_duration(duration)}\n"
                f"Estimated Processing Time: "
                f"{low}-{high} minutes"
            )

            self.update_validation(
                validation_text
            )

            if not valid:

                self.root.after(
                    0,
                    lambda:
                    messagebox.showerror(
                        "Video Validation Error",
                        message
                    )
                )

                return

            #print(message)            
            
            self.update_status(
                "Loading Model..."
            )

            if self.transcriber is None:

                self.transcriber = (
                    Transcriber()
                )

            self.update_status(
                "Transcribing..."
            )

            segments, info = (
                self.transcriber.transcribe(
                    self.video_path.get()
                )
            )
            #print("Segments type:", type(segments))
            #print("Segments count:", len(segments))

            if segments:
                #print("First segment:", segments[0])
                pass

            srt_file = save_srt(
                self.video_path.get(),
                segments
            )


            self.update_language(
                info.language
            )

            self.clear_preview()

            for segment in segments:

                self.add_preview_text(
                    segment.text.strip()
                )

            self.update_status(
                "Completed"
            )

            self.root.after(
                0,
                lambda:
                messagebox.showinfo(
                    "Subtitle Saved",
                    f"SRT File Created:\n\n{srt_file}"
                )
            )

        except Exception as ex:

            self.root.after(
                0,
                lambda:
                messagebox.showerror(
                    "Error",
                    str(ex)
                )
            )

            self.update_status(
                "Failed"
            )

        finally:

            self.root.after(
                0,
                lambda:
                self.generate_btn.config(
                    state="normal"
                )
            )

    # ----------------------------------
    # Status
    # ----------------------------------
    def update_language(self, language):

        self.root.after(
            0,
            lambda:
            self.language_label.config(
                text=
                f"Detected Language: {language}"
            )
        )

    def clear_preview(self):

        self.root.after(
            0,
            lambda:
            self.preview.delete(
                "1.0",
                tk.END
            )
        )

    def add_preview_text(self, text):

        self.root.after(
            0,
            lambda:
            self.preview.insert(
                tk.END,
                text + "\n"
            )
        )

    def update_validation(self, text):

        self.root.after(
            0,
            lambda:
            self.validation_label.config(
                text=text
            )
        )

    def update_status(self, text):

        self.root.after(
            0,
            lambda:
            self.status_label.config(
                text=text
            )
        )