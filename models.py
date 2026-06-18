from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ChecklistRule:
    number: int
    concept: str
    reference: str = ""


@dataclass
class ValidationResult:
    number: int
    validation: str
    status: str
    found: Any = None
    expected: Any = None
    source: str = ""
    explanation: str = ""
    evidence: str = ""
    rule: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

