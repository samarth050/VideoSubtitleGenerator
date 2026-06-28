import tkinter as tk
import os
import vlc

from video.timecode import TimeCode

class VideoPlayer(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent)

        #
        # VLC
        #

        self.instance = vlc.Instance()

        self.player = self.instance.media_player_new()

        #
        # Build GUI
        #

        self.build_ui()

    def build_ui(self):

        self.video_area = tk.Frame(
            self,
            bg="black",
            height=320
        )

        self.video_area.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.filename = tk.Label(
            self,
            text="No video loaded"
        )

        self.filename.pack(
            pady=2
        )

        self.status = tk.Label(
            self,
            text="No video loaded",
            fg="blue"
        )

        self.status.pack(
            pady=2
        )

        controls = tk.Frame(self)

        controls.pack(
            fill="x"
        )

        self.play_btn = tk.Button(
            controls,
            text="▶",
            command=self.play
        )

        self.play_btn.pack(
            side=tk.LEFT,
            padx=2
        )

        self.pause_btn = tk.Button(
            controls,
            text="⏸",
            command=self.pause
        )

        self.pause_btn.pack(
            side=tk.LEFT,
            padx=2
        )

        self.stop_btn = tk.Button(
            controls,
            text="■",
            command=self.stop
        )

        self.stop_btn.pack(
            side=tk.LEFT,
            padx=2
        )

        self.position = tk.Label(
            controls,
            text="00:00:00.000"
        )

        self.position.pack(
            side=tk.RIGHT
        )

        self.after(
            100,
            self.attach_player
        )

    def attach_player(self):

        if self.video_area.winfo_id() == 0:

            self.after(
                100,
                self.attach_player
            )

            return

        self.player.set_hwnd(
            self.video_area.winfo_id()
        )

    def load_video(
            self,
            filename):

        self.filename.config(
            text=os.path.basename(filename)
        )

        media = self.instance.media_new(
            filename
        )

        self.player.set_media(
            media
        )

        self.status.config(
            text="Video Loaded"
        )

        self.position.config(
            text="00:00:00.000"
        )

    def seek(
            self,
            milliseconds):

        self.player.set_time(
            milliseconds
        )

        self.position.config(
            text=TimeCode.format(
                milliseconds
            )
        )

        self.status.config(
            text="Seek"
        )

    def play(self):

        self.player.play()

        self.status.config(
            text="Playing"
        )

    def pause(self):

        self.player.pause()

        self.status.config(
            text="Paused"
        )

    def stop(self):

        self.player.stop()

        self.status.config(
            text="Stopped"
        )

        self.position.config(
            text="00:00:00.000"
        )


    def current_time(self):
        return 0


    def duration(self):
        return 0


    def previous(self):
        pass    