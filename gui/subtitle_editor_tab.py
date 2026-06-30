import os
import tkinter as tk
from tkinter import ttk
from services.subtitle_validator import (
    SubtitleValidator
)
from video.timecode import TimeCode
from video.video_controller import VideoController
from services.subtitle_parser import SubtitleParser

from tkinter import filedialog
from video.video_player import VideoPlayer
from tkinter import messagebox

from tkinter.scrolledtext import ScrolledText


class SubtitleEditorTab(tk.Frame):

    def __init__(
            self,
            parent,
            project):

        super().__init__(parent)

        self.project = project
        self.current_file = None
        self.current_video = None

        self.modified = False
        self.subtitles = []

        self.current_index = -1

        #
        # Playback synchronization
        #

        self.current_highlight = -1

        self.updating_from_video = False

        self.build_ui()

        self.after(
            250,
            self.update_video_position
        )

    def highlight_current_subtitle(
            self,
            milliseconds):

        for index, subtitle in enumerate(self.subtitles):

            start = TimeCode.timestamp_to_ms(
                subtitle.start
            )

            end = TimeCode.timestamp_to_ms(
                subtitle.end
            )

            if start <= milliseconds <= end:

                if index == self.current_highlight:

                    return

                self.current_highlight = index

                self.updating_from_video = True

                self.subtitle_tree.selection_set(
                    str(index)
                )

                self.subtitle_tree.focus(
                    str(index)
                )

                self.subtitle_tree.see(
                    str(index)
                )

                self.on_select(None)

                self.updating_from_video = False

                return

    def build_ui(self):

        #
        # ----------------------------------------------------------
        # Project Information
        # ----------------------------------------------------------
        #

        project_frame = tk.LabelFrame(

            self,

            text="Current Project"

        )

        project_frame.pack(

            fill="x",

            padx=10,

            pady=5

        )

        #
        # Video
        #

        tk.Label(

            project_frame,

            text="Video :",

            width=12,

            anchor="w"

        ).grid(

            row=0,

            column=0,

            padx=5,

            pady=2,

            sticky="w"

        )

        self.video_label = tk.Label(

            project_frame,

            text="No video loaded",

            anchor="w"

        )

        self.video_label.grid(

            row=0,

            column=1,

            sticky="w"

        )

        #
        # Subtitle
        #

        tk.Label(

            project_frame,

            text="Subtitle :",

            width=12,

            anchor="w"

        ).grid(

            row=1,

            column=0,

            padx=5,

            pady=2,

            sticky="w"

        )

        self.subtitle_label = tk.Label(

            project_frame,

            text="No subtitle loaded",

            anchor="w"

        )

        self.subtitle_label.grid(

            row=1,

            column=1,

            sticky="w"

        )

        #
        # Folder
        #

        tk.Label(

            project_frame,

            text="Folder :",

            width=12,

            anchor="w"

        ).grid(

            row=2,

            column=0,

            padx=5,

            pady=2,

            sticky="w"

        )

        self.folder_label = tk.Label(

            project_frame,

            text="",

            anchor="w"

        )

        self.folder_label.grid(

            row=2,

            column=1,

            sticky="w"

        )

        #
        # Project Status
        #

        tk.Label(

            project_frame,

            text="Status :",

            width=12,

            anchor="w"

        ).grid(

            row=3,

            column=0,

            padx=5,

            pady=2,

            sticky="w"

        )

        self.project_status = tk.Label(

            project_frame,

            text="Ready",

            anchor="w"

        )

        self.project_status.grid(

            row=3,

            column=1,

            sticky="w"

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
            text="Open Video",
            command=self.browse_video
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Open Subtitle",
            command=self.browse_subtitle
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

        tk.Button(
            button_frame,
            text="Validate",
            command=self.validate_subtitles
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Find",
            command=self.find_text
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Replace",
            command=self.replace_text
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
            columns=(
                "number",
                "start",
                "end",
                "preview"
            ),
            show="headings"
        )

        self.subtitle_tree.heading(
            "number",
            text="No"
        )

        self.subtitle_tree.heading(
            "start",
            text="Start"
        )

        self.subtitle_tree.heading(
            "end",
            text="End"
        )

        self.subtitle_tree.heading(
            "preview",
            text="Preview"
        )

        self.subtitle_tree.column(
            "number",
            width=50,
            anchor="center"
        ) 

        self.subtitle_tree.column(
            "start",
            width=90
        )

        self.subtitle_tree.column(
            "end",
            width=90
        )

        self.subtitle_tree.column(
            "preview",
            width=260
        )


        self.subtitle_tree.pack(
            fill="both",
            expand=True
        )

        self.subtitle_tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )

        self.bind_all(
            "<Control-Right>",
            lambda e: self.next_subtitle()
        )

        self.bind_all(
            "<Control-Left>",
            lambda e: self.previous_subtitle()
        )

        self.bind_all(
            "<Control-s>",
            lambda e: self.save()
        )

        self.subtitle_tree.bind(
            "<Double-1>",
            self.on_select
        )

        # =================================================
        # CENTER PANEL
        # =================================================
        center = tk.Frame(self.paned)
        self.paned.add(
            center,
            width=450
        )

        tk.Label(
            center,
            text="Video Preview",
            font=("Segoe UI", 10, "bold")
        ).pack(
            pady=5
        )
        self.video_player = VideoPlayer(
            center
        )
        self.video_controller = VideoController(
            self.video_player
        )
        
        self.video_player.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.video_time = tk.Label(
            center,
            text="00:00:00.000"
        )

        self.video_time.pack(
            pady=5
        )

        controls = tk.Frame(center)

        controls.pack(
            pady=5
        )

        tk.Button(
            controls,
            text="◀",
            width=4
        ).pack(
            side=tk.LEFT,
            padx=2
        )

        tk.Button(
            controls,
            text="▶",
            width=4
        ).pack(
            side=tk.LEFT,
            padx=2
        )

        tk.Button(
            controls,
            text="⏸",
            width=4
        ).pack(
            side=tk.LEFT,
            padx=2
        )

        tk.Button(
            controls,
            text="■",
            width=4
        ).pack(
            side=tk.LEFT,
            padx=2
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        right = tk.Frame(self.paned)

        self.paned.add(
            right,
            width=450
        )

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

        self.start_entry = tk.Entry(
            right,
            textvariable=self.start_var
        )

        self.start_entry.pack(
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

        self.end_entry = tk.Entry(
            right,
            textvariable=self.end_var
        )

        self.end_entry.pack(
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

        self.text_editor.bind(
            "<<Modified>>",
            self.text_changed
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

    def browse_video(self):

        filename = filedialog.askopenfilename(

            title="Open Video",

            filetypes=[

                (
                    "Video Files",

                    "*.mp4 *.mkv *.avi *.mov *.wmv *.mpeg *.mpg"
                ),

                ("All Files", "*.*")

            ]

        )

        if not filename:

            return

        self.load_video(filename)

    def update_video_position(self):

        try:

            if (
                self.video_controller.is_playing()
                and
                self.subtitles
            ):

                milliseconds = (
                    self.video_controller.current_time()
                )

                self.highlight_playing_subtitle(
                    milliseconds
                )

        finally:

            self.after(
                250,
                self.update_video_position
            )

    def highlight_playing_subtitle(
            self,
            milliseconds):

        for index, subtitle in enumerate(self.subtitles):

            start = TimeCode.timestamp_to_ms(
                subtitle.start
            )

            end = TimeCode.timestamp_to_ms(
                subtitle.end
            )

            if start <= milliseconds <= end:

                if index == self.current_highlight:
                    return

                self.current_highlight = index

                self.updating_from_video = True

                self.subtitle_tree.selection_set(
                    str(index)
                )

                self.subtitle_tree.focus(
                    str(index)
                )

                self.subtitle_tree.see(
                    str(index)
                )

                self.load_subtitle(index)

                self.updating_from_video = False

                return


    def browse_subtitle(self):

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
        self.project.subtitle_file = filename

        self.subtitle_label.config(
            text=os.path.basename(filename)
        )

        self.folder_label.config(
            text=os.path.dirname(filename)
        )

        self.project.subtitles = SubtitleParser.load(
            filename
        )
        self.subtitles = self.project.subtitles
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
                values=(
                    subtitle.number,
                    subtitle.start,
                    subtitle.end,
                    preview
                )
            )

        self.status.config(
            text=f"Loaded {len(self.subtitles)} subtitles"
        )

        if self.subtitles:

            self.subtitle_tree.selection_set("0")

            self.on_select(None)

        video = self.find_matching_video(
            filename
        )

        if video:

            self.load_video(video)            

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
            text=(
                f"Saved successfully   |   "
                f"{len(self.subtitles)} subtitles"
            )
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

            self.project.subtitle_file = filename

            self.save()

    def validate_subtitles(self):

        self.save_current()

        report = SubtitleValidator.validate(
            self.subtitles
        )

        if report.valid:

            messagebox.showinfo(
                "Validation",
                "No validation errors found."
            )

            self.status.config(
                text="Validation successful"
            )

            return

        first = report.issues[0]

        subtitle_number = first.subtitle_number

        if first.field == "start":

            self.start_entry.configure(
                bg="#ffd6d6"
            )

        elif first.field == "end":

            self.end_entry.configure(
                bg="#ffd6d6"
            )

        elif first.field == "text":

            self.text_editor.configure(
                bg="#fff0d6"
            )


        message = "\n\n".join(

            f"[{issue.severity}] "
            f"Subtitle {issue.subtitle_number}\n"
            f"Issue : {issue.message}\n"
            f"Suggested Fix : {issue.suggested_fix}"

            for issue in report.issues

        )

        messagebox.showwarning(
            "Validation Report",
            message
        )

        for index, subtitle in enumerate(self.subtitles):

            if subtitle.number == subtitle_number:

                self.subtitle_tree.selection_set(
                    str(index)
                )

                self.subtitle_tree.see(
                    str(index)
                )

                self.on_select(None)

                break

        self.status.config(
            text=f"{len(report.issues)} validation issue(s) ({report.error_count} errors)"
        )


    def find_text(self):
        pass


    def replace_text(self):
        pass

    def on_select(self, event):

        if self.updating_from_video:

            return

        self.start_entry.configure(
            bg="white"
        )

        self.end_entry.configure(
            bg="white"
        )

        if self.current_index != -1:
            self.save_current()   
        selected = self.subtitle_tree.selection()

        if not selected:
            return

        self.current_index = int(
            selected[0]
        )

        subtitle = self.subtitles[
            self.current_index
        ]

        milliseconds = TimeCode.timestamp_to_ms(
            subtitle.start
        )

        self.video_controller.seek(
            milliseconds
        )

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
        self.text_editor.focus_set()

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
            text=(
                f"Subtitle {subtitle.number} "
                f"of {len(self.subtitles)}   |   "
                f"Modified"
            )
        )
        preview = subtitle.text.replace(
            "\n",
            " "
        )

        if len(preview) > 45:
            preview = preview[:45] + "..."

        self.subtitle_tree.item(
            str(self.current_index),
            values=(
                subtitle.number,
                subtitle.start,
                subtitle.end,
                preview
            )
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

    def text_changed(self, event):

        if self.text_editor.edit_modified():

            self.modified = True

            self.status.config(
                text="Modified"
            )

            self.text_editor.edit_modified(False)

    def load_video(
            self,
            filename):

        self.project.video_file = filename

        self.video_controller.load(
            filename
        )

    def load_subtitle(
            self,
            index):

        subtitle = self.subtitles[index]

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

        self.status.config(
            text=
            f"Subtitle "
            f"{subtitle.number} "
            f"of "
            f"{len(self.subtitles)}"
        )

    def find_matching_video(
            self,
            subtitle_file):

        folder = os.path.dirname(subtitle_file)

        subtitle_name = os.path.splitext(
            os.path.basename(subtitle_file)
        )[0].lower()

        video_extensions = (
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".mpeg",
            ".mpg"
        )

        #
        # Search every video in the folder
        #

        for filename in os.listdir(folder):

            name, ext = os.path.splitext(filename)

            if ext.lower() not in video_extensions:

                continue

            video_name = name.lower()

            #
            # Exact match
            #

            if video_name == subtitle_name:

                return os.path.join(
                    folder,
                    filename
                )

            #
            # Subtitle starts with video name
            #

            if subtitle_name.startswith(video_name):

                return os.path.join(
                    folder,
                    filename
                )

        return None