from dataclasses import dataclass, field

from services.subtitle_parser import SubtitleEntry


@dataclass
class SubtitleProject:
    """
    Represents one subtitle editing project.
    """

    #
    # Files
    #

    video_file: str = ""

    subtitle_file: str = ""

    #
    # Data
    #

    subtitles: list[SubtitleEntry] = field(
        default_factory=list
    )

    #
    # Editor State
    #

    modified: bool = False

    current_index: int = -1

    #
    # Playback State
    #

    current_position: int = 0

    duration: int = 0

    playing: bool = False