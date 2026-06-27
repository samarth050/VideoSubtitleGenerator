import re
from models.validation_issue import ValidationIssue
from models.validation_report import (
    ValidationReport
)

class SubtitleValidator:

    TIMESTAMP_PATTERN = re.compile(
        r"^\d{2}:\d{2}:\d{2},\d{3}$"
    )

    @staticmethod
    def timestamp_to_ms(timestamp):

        hh, mm, rest = timestamp.split(":")

        ss, ms = rest.split(",")

        return (
            int(hh) * 3600000
            + int(mm) * 60000
            + int(ss) * 1000
            + int(ms)
        )

    @classmethod
    def validate(cls, subtitles):

        report = ValidationReport()

        report.checked_subtitles = len(
            subtitles
        ) 

        previous_end = None

        expected_number = 1

        numbers = set()

        for subtitle in subtitles:

            #
            # Number
            #

            if subtitle.number != expected_number:

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Error",
                        message=f"Expected subtitle number {expected_number}",
                        field="number",
                        fixable=True
                    )
                )

            expected_number += 1

            #
            # Duplicate Number
            #

            if subtitle.number in numbers:

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Error",
                        message="Duplicate subtitle number",
                        field="number",
                        fixable=True,
                        suggested_fix="Use Renumber Subtitles."
                    )
                )

            numbers.add(
                subtitle.number
            )

            #
            # Empty Text
            #

            if not subtitle.text.strip():

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Warning",
                        message="Empty subtitle text",
                        field="text",
                        fixable=False,
                        suggested_fix="Enter subtitle text or delete the subtitle."
                    )
                )

            #
            # Timestamp Format
            #

            if not cls.TIMESTAMP_PATTERN.match(
                    subtitle.start):

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Error",
                        message="Invalid start time",
                        field="start",
                        fixable=False,
                        suggested_fix="Use HH:MM:SS,mmm format (e.g. 00:01:15,250)"
                    )
                )

            if not cls.TIMESTAMP_PATTERN.match(
                    subtitle.end):

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Error",
                        message="Invalid end time",
                        field="end",
                        fixable=False,
                        suggested_fix="Use HH:MM:SS,mmm format (e.g. 00:01:18,900)"
                    )
                )

            #
            # Time Order
            #

            try:

                start_ms = cls.timestamp_to_ms(
                    subtitle.start
                )

                end_ms = cls.timestamp_to_ms(
                    subtitle.end
                )

                if end_ms <= start_ms:

                    report.issues.append(
                        ValidationIssue(
                            subtitle_number=subtitle.number,
                            severity="Error",
                            message="End time before start time",
                            field="end",
                            fixable=False,
                            suggested_fix="Set the end time later than the start time."
                        )
                    )

                if (
                    previous_end is not None
                    and
                    start_ms < previous_end
                ):

                    report.issues.append(
                        ValidationIssue(
                            subtitle_number=subtitle.number,
                            severity="Error",
                            message="Overlaps previous subtitle",
                            field="end",
                            fixable=False
                        )
                    )

                previous_end = end_ms

            except Exception:

                pass

            #
            # Text Length
            #

            lines = subtitle.text.splitlines()

            if len(lines) > 2:

                report.issues.append(
                    ValidationIssue(
                        subtitle_number=subtitle.number,
                        severity="Warning",
                        message="More than two lines",
                        field="text",
                        fixable=True,
                        suggested_fix="Split the subtitle into two subtitle entries."
                    )
                )

            for line in lines:

                if len(line) > 42:

                    report.issues.append(
                        ValidationIssue(
                            subtitle_number=subtitle.number,
                            severity="Warning",
                            message="Line exceeds 42 characters",
                            field="text",
                            fixable=True,
                            suggested_fix="Split the text into two shorter lines."
                        )
                    )
        report.error_count = sum(

            1

            for issue in report.issues

            if issue.severity == "Error"

        )

        report.warning_count = sum(

            1

            for issue in report.issues

            if issue.severity == "Warning"

        )

        report.valid = (

            report.error_count == 0

        )                    
        return report