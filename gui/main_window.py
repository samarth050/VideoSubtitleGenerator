import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from gui.generate_tab import GenerateTab
from gui.subtitle_editor_tab import SubtitleEditorTab
from gui.transcript_tab import TranscriptTab
from gui.settings_tab import SettingsTab
from gui.about_tab import AboutTab

class MainWindow:

    def __init__(self, root):

        self.root = root

        root.title("Video Subtitle Generator")

        root.geometry("1100x750")

        self.notebook = ttk.Notebook(root)

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.generate_tab = GenerateTab(
            self.notebook
        )

        self.editor_tab = SubtitleEditorTab(
            self.notebook
        )

        self.generate_tab.on_srt_created = (
            self.open_generated_srt
        )

        self.transcript_tab = TranscriptTab(
            self.notebook
        )

        self.settings_tab = SettingsTab(
            self.notebook
        )

        self.about_tab = AboutTab(
            self.notebook
        )

        self.notebook.add(
            self.generate_tab,
            text="Generate"
        )

        self.notebook.add(
            self.editor_tab,
            text="Subtitle Editor"
        )

        self.notebook.add(
            self.transcript_tab,
            text="Transcript"
        )

        self.notebook.add(
            self.settings_tab,
            text="Settings"
        )

        self.notebook.add(
            self.about_tab,
            text="About"
        )

    def open_generated_srt(
            self,
            video_file,
            srt_file):

        self.editor_tab.load_video(
            video_file
        )

        self.editor_tab.load_file(
            srt_file
        )

        self.notebook.select(
            self.editor_tab
        )

 











