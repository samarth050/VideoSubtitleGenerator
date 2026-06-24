import subprocess
import json


class VideoValidator:

    @staticmethod
    def get_media_info(video_file):

        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            video_file
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return json.loads(result.stdout)

    @staticmethod
    def validate(video_file):

        try:

            media_info = (
                VideoValidator.get_media_info(
                    video_file
                )
            )

            streams = media_info.get(
                "streams",
                []
            )

            video_streams = [
                s for s in streams
                if s.get("codec_type") == "video"
            ]

            audio_streams = [
                s for s in streams
                if s.get("codec_type") == "audio"
            ]

            if len(audio_streams) == 0:
                return (
                    False,
                    "No audio stream found."
                )

            ok, error = (
                VideoValidator.test_audio_decode(
                    video_file
                )
            )

            if not ok:

                return (
                    False,
                    "Audio stream appears damaged "
                    "or cannot be decoded."
                )

            return (
                True,
                f"Video OK. "
                f"Found {len(audio_streams)} audio stream(s)."
            )

        except Exception as ex:

            return (
                False,
                f"Validation failed:\n{str(ex)}"
            )

    @staticmethod
    def test_audio_decode(video_file):

        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", video_file,
            "-t", "5",
            "-vn",
            "-f", "null",
            "-"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return (
            result.returncode == 0,
            result.stderr
        )
    
    @staticmethod
    def get_duration(video_file):

        media_info = (
            VideoValidator.get_media_info(
                video_file
            )
        )

        duration = float(
            media_info["format"]["duration"]
        )

        return duration   

    @staticmethod
    def format_duration(seconds):

        hours = int(seconds // 3600)

        minutes = int(
            (seconds % 3600) // 60
        )

        seconds = int(seconds % 60)

        return (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{seconds:02}"
        )

    @staticmethod
    def estimate_processing_time(
            duration_seconds,
            model_name="base"):

        duration_minutes = (
            duration_seconds / 60
        )

        factors = {
            "tiny": 0.10,
            "base": 0.25,
            "small": 0.40,
            "medium": 0.70,
            "large-v3": 1.20
        }

        factor = factors.get(
            model_name,
            0.25
        )

        estimate = (
            duration_minutes * factor
        )

        low = int(estimate * 0.8)
        high = int(estimate * 1.2)

        return (
            low,
            high
        )                     