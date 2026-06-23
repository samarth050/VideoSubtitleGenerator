from pathlib import Path


def format_timestamp(seconds):

    milliseconds = int(
        (seconds - int(seconds))
        * 1000
    )

    seconds = int(seconds)

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    seconds = seconds % 60

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{seconds:02},"
        f"{milliseconds:03}"
    )


def save_srt(
        video_file,
        segments):

    video_path = Path(video_file)

    srt_file = (
        video_path.parent /
        f"{video_path.stem}.en.srt"
    )

    with open(
        srt_file,
        "w",
        encoding="utf-8"
    ) as f:

        for index, segment in enumerate(
                segments,
                start=1):

            f.write(
                f"{index}\n"
            )

            f.write(
                f"{format_timestamp(segment.start)}"
                f" --> "
                f"{format_timestamp(segment.end)}\n"
            )

            f.write(
                segment.text.strip()
            )

            f.write("\n\n")

    return str(srt_file)