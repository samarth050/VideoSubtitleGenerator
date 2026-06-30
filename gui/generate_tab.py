import tkinter as tk
import time
import threading
from services.subtitle_workflow import SubtitleWorkflow
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText


class GenerateTab(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent)

        # ---------------------------------
        # Data
        # ---------------------------------

        self.workflow = SubtitleWorkflow()

        # ---------------------------------
        # Tk Variables
        # ---------------------------------

        self.video_path = tk.StringVar()

        self.selected_model = tk.StringVar(
            value="small"
        )

        # ---------------------------------
        # Runtime Variables
        # ---------------------------------

        
        self.start_time: float | None = None
        self.generated_srt = None
        self.on_srt_created = None
        #
        # Cancellation
        #

        self.cancel_requested = False        
        # ---------------------------------
        # Build User Interface
        # ---------------------------------

        self.build_ui()

    def build_ui(self):

        # -------------------------
        # Video File
        # -------------------------

        tk.Label(
            self,
            text="Video File"
        ).pack(pady=5)

        tk.Entry(
            self,
            textvariable=self.video_path,
            width=100
        ).pack()

        tk.Button(
            self,
            text="Browse",
            command=self.browse
        ).pack(pady=5)

        self.file_label = tk.Label(
            self,
            text="No file selected"
        )

        self.file_label.pack()

        tk.Label(
            self,
            text="Whisper Model"
        ).pack()

        model_frame = tk.Frame(self)
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
            self,
            text="Recommended - Good balance of speed and accuracy"
        )

        self.selected_model.trace_add(
            "write",
            self.on_model_change
        )        

        self.model_info_label.pack()        

        button_frame = tk.Frame(self)
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

        self.cancel_btn = tk.Button(

            button_frame,

            text="Cancel",

            command=self.cancel_transcription,

            state="disabled"

        )

        self.cancel_btn.pack(

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
            self,
            text="Ready"
        )

        self.status_label.pack()


        # -------------------------
        # Validation Message
        # -------------------------

        self.validation_label = tk.Label(
            self,
            text="",
            wraplength=900,
            justify="left"
        )

        self.validation_label.pack()

        # -------------------------
        # Language
        # -------------------------

        self.language_label = tk.Label(
            self,
            text="Detected Language: Unknown"
        )

        self.language_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            self,
            orient="horizontal",
            length=500,
            mode="determinate",
            maximum=100
        )

        self.progress_bar.pack(pady=5)

        self.time_label = tk.Label(
            self,
            text="Elapsed: 00:00   Remaining: --:--"
        )

        self.time_label.pack()        

        # -------------------------
        # Transcript Preview
        # -------------------------

        self.preview = ScrolledText(
            self,
            width=120,
            height=30
        )

        self.preview.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

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

    def update_progress(self, percent):

        self.after(
            0,
            lambda: self.progress_bar.configure(
                value=percent
            )
        )

    def update_status(self, text):

        self.after(
            0,
            lambda:
            self.status_label.config(
                text=text
            )
        )
        
    def update_validation(self, text):

        self.after(
            0,
            lambda:
            self.validation_label.config(
                text=text
            )
        )

    def update_language(self, language):

        self.after(
            0,
            lambda:
            self.language_label.config(
                text=
                f"Detected Language: {language}"
            )
        )

    def clear_preview(self):

        self.after(
            0,
            lambda:
            self.preview.delete(
                "1.0",
                tk.END
            )
        )

    def add_preview_text(self, text):

        self.after(
            0,
            lambda:
            self.preview.insert(
                tk.END,
                text + "\n"
            )
        )

    def update_time(
            self,
            percent):
        if self.start_time is None:
            return

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

        self.after(
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

    def cancel_transcription(self):

        self.cancel_requested = True

        self.cancel_btn.config(
            state="disabled"
        )

        self.update_status(
            "Cancelling..."
        )

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

        self.cancel_requested = False

        self.cancel_btn.config(
            state="normal"
        )

        thread = threading.Thread(
            target=self.transcribe_video,
            daemon=True
        )
        thread.start()

    # ----------------------------------
    # Actual Processing
    # ----------------------------------

    def transcribe_video(self):

        try:

            self.update_status(
                "Validating Video..."
            )

            result = self.workflow.validate(
                self.video_path.get(),
                self.selected_model.get()
            )

            validation_text = (
                f"Model: "
                f"{self.selected_model.get().upper()}\n"
                f"{result.message}\n"
                f"File Size: "
                f"{result.size_gb:.2f} GB\n"
                f"Duration: "
                f"{self.workflow.format_duration(result.duration)}\n"
                f"Estimated Processing Time: "
                f"{result.estimate_low}-{result.estimate_high} minutes"
            )

            self.update_validation(
                validation_text
            )

            if not result.valid:

                self.after(
                    0,
                    lambda:
                    messagebox.showerror(
                        "Video Validation Error",
                        result.message
                    )
                )

                return

            #print(message)            
            
            self.update_status(
                "Loading Model..."
            )
        

            self.update_status(
                "Transcribing..."
            )

            self.start_time = time.time()

            segments_generator, info = (
                self.workflow.transcribe(
                    self.video_path.get(),
                    self.selected_model.get()
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

                #
                # User pressed Cancel
                #

                if self.cancel_requested:

                    self.update_status(
                        "Cancelled"
                    )

                    self.after(
                        0,
                        lambda:
                        messagebox.showinfo(
                            "Cancelled",
                            "Subtitle generation cancelled."
                        )
                    )

                    return

                segments.append(segment)

                percent = (
                    segment.end / result.duration
                ) * 100

                self.update_progress(percent)

                self.update_time(percent)

                self.update_status(
                    f"Transcribing... {percent:.1f}%"
                )

                self.add_preview_text(
                    segment.text.strip()
                )
            if self.cancel_requested:

                return
            self.update_progress(100)

            video_file = self.video_path.get()

            srt_file = self.workflow.save(
                video_file,
                segments
            )

            self.generated_srt = srt_file

            # Notify MainWindow that both video and subtitle are ready
            if self.on_srt_created:

                callback = self.on_srt_created

                if callback is not None:

                    self.after(
                        0,
                        lambda: callback(
                            video_file,
                            srt_file
                        )
                    )

            self.update_status(
                "Completed"
            )

            total_time = time.time() - self.start_time

            minutes = int(total_time // 60)
            seconds = int(total_time % 60)

            self.after(
                0,
                lambda:
                self.time_label.config(
                    text=f"Completed in {minutes:02}:{seconds:02}"
                )
            )

            self.after(
                0,
                lambda:
                messagebox.showinfo(
                    "Subtitle Saved",
                    f"SRT File Created:\n\n{srt_file}"
                )
            )

        except Exception as ex:

            self.after(
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

            def finish():

                self.generate_btn.config(
                    state="normal"
                )

                self.cancel_btn.config(
                    state="disabled"
                )

            self.after(
                0,
                finish
            )