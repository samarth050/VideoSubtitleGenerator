from faster_whisper import WhisperModel


class Transcriber:

    def __init__(
            self,
            model_name="small"):

        self.model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, video_file):

        segments, info = self.model.transcribe(
            video_file,
            task="translate",
            beam_size=5
        )

        return list(segments), info