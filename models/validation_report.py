from dataclasses import dataclass, field

from models.validation_issue import ValidationIssue


@dataclass
class ValidationReport:
    """
    Complete subtitle validation report.
    """

    valid: bool = True

    checked_subtitles: int = 0

    error_count: int = 0

    warning_count: int = 0

    issues: list[ValidationIssue] = field(
        default_factory=list
    )