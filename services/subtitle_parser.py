from dataclasses import dataclass


@dataclass
class SubtitleEntry:

    number: int
    start: str
    end: str
    text: str

class SubtitleParser:

    @staticmethod
    def load(filename):

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            data = f.read()

        blocks = data.strip().split("\n\n")

        subtitles = []

        for block in blocks:

            lines = block.splitlines()

            if len(lines) < 3:
                continue

            number = int(lines[0])

            start, end = lines[1].split(" --> ")

            text = "\n".join(lines[2:])

            subtitles.append(
                SubtitleEntry(
                    number,
                    start,
                    end,
                    text
                )
            )

        return subtitles