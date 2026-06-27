from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """
    Represents a single subtitle validation issue.
    """

    subtitle_number: int

    severity: str
    # Error, Warning, Info

    message: str

    field: str = ""
    # number, start, end, text

    fixable: bool = False

    suggested_fix: str = ""