import os
import tkinter as tk
from tkinter import ttk

from services.subtitle_parser import (
    SubtitleParser,
    SubtitleEntry
)
from tkinter import filedialog

from tkinter import messagebox

from tkinter.scrolledtext import ScrolledText


class SubtitleEditorTab(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent)

        self.current_file = None

        self.modified = False
        self.subtitles = []

        self.current_index = -1        

        self.build_ui()

    def build_ui(self):

        # -------------------------------------------------
        # Subtitle File
        # -------------------------------------------------

        tk.Label(
            self,
            text="Subtitle File"
        ).pack(pady=5)

        self.file_label = tk.Label(
            self,
            text="No subtitle loaded",
            anchor="w"
        )

        self.file_label.pack(
            fill="x",
            padx=10
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_frame = tk.Frame(self)

        button_frame.pack(
            pady=5
        )

        tk.Button(
            button_frame,
            text="Browse",
            command=self.browse
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Save",
            command=self.save
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Save As",
            command=self.save_as
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # -------------------------------------------------
        # Split Window
        # -------------------------------------------------

        self.paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashrelief=tk.RAISED
        )

        self.paned.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # =================================================
        # LEFT PANEL
        # =================================================

        left = tk.Frame(self.paned)

        self.paned.add(
            left,
            width=320
        )

        tk.Label(
            left,
            text="Subtitles"
        ).pack()

        self.subtitle_tree = ttk.Treeview(
            left,
            columns=("preview",),
            show="tree headings"
        )

        self.subtitle_tree.heading(
            "#0",
            text="No"
        )

        self.subtitle_tree.heading(
            "preview",
            text="Subtitle Preview"
        )

        self.subtitle_tree.column(
            "#0",
            width=60,
            anchor="center"
        )

        self.subtitle_tree.column(
            "preview",
            width=240
        )

        self.subtitle_tree.pack(
            fill="both",
            expand=True
        )

        self.subtitle_tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        right = tk.Frame(self.paned)

        self.paned.add(right)

        tk.Label(
            right,
            text="Subtitle Number"
        ).pack(
            anchor="w"
        )

        self.number_var = tk.StringVar()

        tk.Entry(
            right,
            textvariable=self.number_var,
            state="readonly"
        ).pack(
            fill="x"
        )

        tk.Label(
            right,
            text="Start Time"
        ).pack(
            anchor="w",
            pady=(10,0)
        )

        self.start_var = tk.StringVar()

        tk.Entry(
            right,
            textvariable=self.start_var
        ).pack(
            fill="x"
        )

        tk.Label(
            right,
            text="End Time"
        ).pack(
            anchor="w",
            pady=(10,0)
        )

        self.end_var = tk.StringVar()

        tk.Entry(
            right,
            textvariable=self.end_var
        ).pack(
            fill="x"
        )

        tk.Label(
            right,
            text="Subtitle Text"
        ).pack(
            anchor="w",
            pady=(10,0)
        )

        self.text_editor = ScrolledText(
            right,
            undo=True,
            height=12
        )

        self.text_editor.pack(
            fill="both",
            expand=True
        )

        # -------------------------------------------------
        # Navigation Buttons
        # -------------------------------------------------

        nav = tk.Frame(right)

        nav.pack(
            pady=5
        )

        tk.Button(
            nav,
            text="Previous",
            command=self.previous_subtitle
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            nav,
            text="Save Subtitle",
            command=self.save_current
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            nav,
            text="Next",
            command=self.next_subtitle
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # -------------------------------------------------
        # Status Bar
        # -------------------------------------------------

        self.status = tk.Label(
            self,
            text="Ready",
            anchor="w"
        )

        self.status.pack(
            fill="x"
        )

    def browse(self):

        filename = filedialog.askopenfilename(

            filetypes=[

                ("Subtitle",

                "*.srt")

            ]

        )

        if filename:

            self.load_file(filename)

    def load_file(
            self,
            filename):

        self.current_file = filename

        self.file_label.config(
            text=filename
        )

        self.subtitles = SubtitleParser.load(
            filename
        )

        self.subtitle_tree.delete(
            *self.subtitle_tree.get_children()
        )

        for index, subtitle in enumerate(self.subtitles):

            preview = subtitle.text.replace(
                "\n",
                " "
            )

            if len(preview) > 45:

                preview = preview[:45] + "..."

            self.subtitle_tree.insert(
                "",
                "end",
                iid=str(index),
                text=str(subtitle.number),
                values=(preview,)
            )

        self.status.config(
            text=f"Loaded {len(self.subtitles)} subtitles"
        )

        if self.subtitles:

            self.subtitle_tree.selection_set("0")

            self.on_select(None)

    def save(self):

        if self.current_file is None:
            return

        self.save_current()

        with open(
                self.current_file,
                "w",
                encoding="utf-8"
        ) as f:

            for subtitle in self.subtitles:

                f.write(
                    f"{subtitle.number}\n"
                )

                f.write(
                    f"{subtitle.start} --> {subtitle.end}\n"
                )

                f.write(
                    subtitle.text + "\n\n"
                )

        self.status.config(
            text="Subtitle file saved"
        )

    def save_as(self):

        filename = filedialog.asksaveasfilename(

            defaultextension=".srt",

            filetypes=[

                ("Subtitle",

                "*.srt")

            ]

        )

        if filename:

            self.current_file = filename

            self.save()


    def on_select(self, event):

        selected = self.subtitle_tree.selection()

        if not selected:
            return

        self.current_index = int(
            selected[0]
        )

        subtitle = self.subtitles[
            self.current_index
        ]

        self.number_var.set(
            subtitle.number
        )

        self.start_var.set(
            subtitle.start
        )

        self.end_var.set(
            subtitle.end
        )

        self.text_editor.delete(
            "1.0",
            tk.END
        )

        self.text_editor.insert(
            "1.0",
            subtitle.text
        )


    def save_current(self):

        if self.current_index < 0:
            return

        subtitle = self.subtitles[
            self.current_index
        ]

        subtitle.start = self.start_var.get()

        subtitle.end = self.end_var.get()

        subtitle.text = self.text_editor.get(
            "1.0",
            tk.END
        ).strip()

        self.status.config(
            text=f"Subtitle {subtitle.number} updated"
        )


    def previous_subtitle(self):

        if self.current_index <= 0:
            return

        self.save_current()

        self.current_index -= 1

        self.subtitle_tree.selection_set(
            str(self.current_index)
        )

        self.on_select(None)


    def next_subtitle(self):

        if self.current_index >= len(self.subtitles)-1:
            return

        self.save_current()

        self.current_index += 1

        self.subtitle_tree.selection_set(
            str(self.current_index)
        )

        self.on_select(None)          