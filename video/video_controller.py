class VideoController:

    def __init__(self, player):

        self.player = player

        self.current_video = None

    def load(self, filename):

        self.current_video = filename

        self.player.load_video(filename)

    def play(self):

        print("VideoController : Play")

        self.player.play()

    def pause(self):

        print("VideoController : Pause")

        self.player.pause()

    def stop(self):

        print("VideoController : Stop")

        self.player.stop()

    def seek(self, milliseconds):

        print(
            "Seek to",
            milliseconds
        )

        self.player.seek(
            milliseconds
        )

    def current_time(self):

        return self.player.current_time()

    def duration(self):

        return self.player.duration()
    
    def is_playing(self):

        return self.player.is_playing()    