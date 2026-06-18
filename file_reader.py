from __future__ import annotations

from io import BytesIO
from pathlib import Path
import pandas as pd
try:
    from pypdf import PdfReader
except ImportError:  # Compatibilidad con el entorno inicial de la POC.
    PdfReader = None
    import pdfplumber

SUPPORTED_EXTENSIONS = {".md", ".txt", ".csv", ".xlsx", ".xlsm", ".pdf"}


def _bytes(uploaded_file) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()
    if hasattr(uploaded_file, "read"):
        data = uploaded_file.read()
        try: uploaded_file.seek(0)
        except Exception: pass
        return data
    return Path(uploaded_file).read_bytes()


def _name(uploaded_file) -> str:
    return getattr(uploaded_file, "name", str(uploaded_file))


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try: return data.decode(encoding)
        except UnicodeDecodeError: continue
    return data.decode("utf-8", errors="replace")


def _compact_frame(frame: pd.DataFrame) -> str:
    frame = frame.dropna(how="all").dropna(axis=1, how="all")
    if frame.empty: return "[Hoja sin datos legibles]"
    frame = frame.fillna("").astype(str).map(lambda value: " ".join(value.split()))
    return frame.to_csv(index=False, header=False, lineterminator="\n")


def read_uploaded_file(uploaded_file) -> str:
    """Extrae un archivo cargado a texto compacto y trazable para Gemini."""
    name = _name(uploaded_file)
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: {suffix or 'sin extensión'}")
    data = _bytes(uploaded_file)
    if not data: raise ValueError(f"El archivo {name} está vacío.")

    if suffix in {".md", ".txt", ".csv"}:
        return f"ARCHIVO: {name}\n{_decode(data)}"
    if suffix in {".xlsx", ".xlsm"}:
        sheets = pd.read_excel(BytesIO(data), sheet_name=None, header=None, engine="openpyxl")
        sections = [f"ARCHIVO: {name}"]
        for sheet_name, frame in sheets.items():
            sections.extend((f"\n=== HOJA: {sheet_name} ===", _compact_frame(frame)))
        return "\n".join(sections)

    pages = [f"ARCHIVO: {name}"]
    if PdfReader:
        reader = PdfReader(BytesIO(data))
        extracted = (page.extract_text() for page in reader.pages)
    else:
        pdf = pdfplumber.open(BytesIO(data))
        extracted = (page.extract_text() for page in pdf.pages)
    for number, text in enumerate(extracted, 1):
        pages.extend((f"\n=== PÁGINA {number} ===", text or "[Sin texto extraíble]"))
    if not PdfReader: pdf.close()
    return "\n".join(pages)
