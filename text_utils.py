import re
import unicodedata
from typing import Any


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))


def money(value: Any):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return int(round(value))
    raw = re.sub(r"[^0-9-]", "", str(value))
    return int(raw) if raw not in ("", "-") else None


def names_equivalent(a: Any, b: Any) -> bool:
    stop = {"DE", "DEL", "LA", "EL", "S", "A", "SA", "ESP", "SIGLA", "GEB"}
    ta = {x for x in normalize_text(a).split() if x not in stop}
    tb = {x for x in normalize_text(b).split() if x not in stop}
    return bool(ta and tb and (ta <= tb or tb <= ta or len(ta & tb) / max(len(ta), len(tb)) >= .8))

