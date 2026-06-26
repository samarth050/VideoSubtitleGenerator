import os
from services.transcription import Transcriber
from services.subtitle_writer import save_srt
from services.video_validator import VideoValidator
from models.validation_result import ValidationResult

class SubtitleWorkflow:

    def __init__(self):

        self.transcriber = None
        self.current_model = None

    def get_transcriber(
        self,
        model_name):

        if (
            self.transcriber is None
            or
            self.current_model != model_name
        ):

            self.current_model = model_name

            self.transcriber = Transcriber(
                model_name
            )

        return self.transcriber

    def validate(
            self,
            video_file,
            model_name):

        valid, message = (
            VideoValidator.validate(
                video_file
            )
        )

        duration = (
            VideoValidator.get_duration(
                video_file
            )
        )

        size_gb = (
            os.path.getsize(video_file)
            / (1024 ** 3)
        )

        low, high = (
            VideoValidator.estimate_processing_time(
                duration,
                model_name
            )
        )

        return ValidationResult(
            valid=valid,
            message=message,
            duration=duration,
            size_gb=size_gb,
            estimate_low=low,
            estimate_high=high
        )

    def transcribe(
            self,
            video_file,
            model_name):
            transcriber = self.get_transcriber(
                model_name
            )

            return transcriber.transcribe(
                video_file
        )

    def save(
            self,
            video_file,
            segments):

        return save_srt(
            video_file,
            segments
        )

    def format_duration(
            self,
            seconds):

        return VideoValidator.format_duration(
            seconds
        )                   