import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import threading
import os
import time
from services.transcription import Transcriber
from services.subtitle_writer import save_srt
from services.video_validator import VideoValidator


class MainWindow:

    def __init__(self, root):

        self.root = root

        root.title("Video Subtitle Generator")

        root.geometry("1000x700")

        self.transcriber = None

        self.current_model = None

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

        # -------------------------
        # Whisper Model
        # -------------------------

        self.selected_model = tk.StringVar(
            value="small"
        )

        tk.Label(
            root,
            text="Whisper Model"
        ).pack()

        model_frame = tk.Frame(root)
        model_frame.pack()

        tk.OptionMenu(
            model_frame,
            self.selected_model,
            "tiny",
            "base",
            "small",
            "medium",
            "large-v3"
        ).pack()

        self.model_info_label = tk.Label(
            root,
            text="Recommended - Good balance of speed and accuracy"
        )

        self.selected_model.trace_add(
            "write",
            self.on_model_change
        )        

        self.model_info_label.pack()        

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.generate_btn = tk.Button(
            button_frame,
            text="Generate English Subtitles",
            command=self.start_transcription
        )

        self.generate_btn.pack(
            side=tk.LEFT,
            padx=5
        )

        self.reset_btn = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_gui
        )

        self.reset_btn.pack(
            side=tk.LEFT,
            padx=5
        )

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

        self.progress_bar = ttk.Progressbar(
            root,
            orient="horizontal",
            length=500,
            mode="determinate",
            maximum=100
        )

        self.progress_bar.pack(pady=5)

        self.time_label = tk.Label(
            root,
            text="Elapsed: 00:00   Remaining: --:--"
        )

        self.time_label.pack()        

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

    def reset_gui(self):

        self.video_path.set("")

        self.file_label.config(
            text="No file selected"
        )

        self.preview.delete(
            "1.0",
            tk.END
        )

        self.status_label.config(
            text="Ready"
        )

        self.validation_label.config(
            text=""
        )

        self.language_label.config(
            text="Detected Language: Unknown"
        )

        self.progress_bar["value"] = 0

        self.time_label.config(
            text="Elapsed: 00:00   Remaining: --:--"
        )

        self.selected_model.set("small")

        self.generate_btn.config(
            state="normal"
        )
        self.progress_bar["value"] = 0

        self.status_label.config(
            text="Ready"
        )

        self.validation_label.config(
            text=""
        )

        self.time_label.config(
            text="Elapsed: 00:00   Remaining: --:--"
        )


    def update_progress(self, percent):

        self.root.after(
            0,
            lambda: self.progress_bar.configure(
                value=percent
            )
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
                        self.selected_model.get()
                    )
            )

            validation_text = (
                f"Model: "
                f"{self.selected_model.get().upper()}\n"
                f"{message}\n"
                f"File Size: "
                f"{size_gb:.2f} GB\n"
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

            if (
                self.transcriber is None
                or
                self.current_model
                !=
                self.selected_model.get()
            ):

                self.current_model = (
                    self.selected_model.get()
                )

                self.transcriber = (
                    Transcriber(
                        self.current_model
                    )
                )            

            self.update_status(
                "Transcribing..."
            )

            self.start_time = time.time()

            segments_generator, info = (
                self.transcriber.transcribe(
                    self.video_path.get()
                )
            )

            segments = []
            #print("Segments type:", type(segments))
            #print("Segments count:", len(segments))

            self.update_language(
                info.language
            )

            self.clear_preview()
            self.update_progress(0)
            for segment in segments_generator:

                segments.append(segment)

                percent = (
                    segment.end / duration
                ) * 100

                self.update_progress(percent)
                self.update_time(percent)

                self.update_status(
                    f"Transcribing... {percent:.1f}%"
                )

                self.add_preview_text(
                    segment.text.strip()
                )

            self.update_progress(100)

            srt_file = save_srt(
                self.video_path.get(),
                segments
            )

            self.update_status(
                "Completed"
            )

            total_time = time.time() - self.start_time

            minutes = int(total_time // 60)
            seconds = int(total_time % 60)

            self.root.after(
                0,
                lambda:
                self.time_label.config(
                    text=f"Completed in {minutes:02}:{seconds:02}"
                )
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

    def update_time(
            self,
            percent):

        if percent <= 0:
            return

        elapsed = time.time() - self.start_time

        remaining = (
            elapsed / percent
        ) * (100 - percent)

        elapsed_minutes = int(elapsed // 60)
        elapsed_seconds = int(elapsed % 60)

        remaining_minutes = int(remaining // 60)
        remaining_seconds = int(remaining % 60)

        self.root.after(
            0,
            lambda:
            self.time_label.config(
                text=
                f"Elapsed: "
                f"{elapsed_minutes:02}:{elapsed_seconds:02}    "
                f"Remaining: "
                f"{remaining_minutes:02}:{remaining_seconds:02}"
            )
        )

    # ----------------------------------
    # Status
    # ----------------------------------

    def on_model_change(self, *args):

        descriptions = {
            "tiny": "Fastest, lowest accuracy",
            "base": "Fast, good quality",
            "small": "Recommended",
            "medium": "High quality",
            "large-v3": "Best quality, slowest"
        }

        self.model_info_label.config(
            text=descriptions.get(
                self.selected_model.get(),
                ""
            )
        )

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