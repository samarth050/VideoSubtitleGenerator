import tkinter as tk


class VideoPlayer(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent)

        self.configure(bg="black")

        tk.Label(
            self,
            text="Video Preview\n(Coming Soon)",
            fg="white",
            bg="black",
            font=("Segoe UI", 14)
        ).pack(
            expand=True,
            fill="both"
        )

    def load_video(self, filename):
        pass

    def seek(self, milliseconds):
        pass

    def play(self):
        pass

    def pause(self):
        pass