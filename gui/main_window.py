import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText


class MainWindow:

    def __init__(self, root):

        self.root = root

        root.title("Video Subtitle Generator")

        root.geometry("1000x700")

        self.video_path = tk.StringVar()

        tk.Label(
            root,
            text="Video File"
        ).pack()

        tk.Entry(
            root,
            textvariable=self.video_path,
            width=100
        ).pack()

        tk.Button(
            root,
            text="Browse",
            command=self.browse
        ).pack()

        tk.Button(
            root,
            text="Generate English Subtitles"
        ).pack(pady=10)

        self.preview = ScrolledText(
            root,
            width=120,
            height=30
        )

        self.preview.pack(
            fill="both",
            expand=True
        )

    def browse(self):

        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Video Files",
                    "*.mp4 *.mkv *.avi *.mov"
                )
            ]
        )

        if filename:
            self.video_path.set(filename)