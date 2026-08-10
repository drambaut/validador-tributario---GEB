from pathlib import Path

ROOT = Path(__file__).resolve().parent / "assets" / "data"

CASES = {
    ("Ciénaga", "ICA anual"): {
        "pdf": ROOT / "Cienaga/GEB - CIENAGA - ICA - 2025.pdf",
        "thomson": [ROOT / "Cienaga/GEB - CIENAGA - ICA - 2025.xlsm"],
        "checklist": ROOT / "Cienaga/Cienaga - Check List Validación Calidad ICA.xlsx",
    },
    ("Ciénaga", "AutoICA + ReteICA mensual"): {
        "pdf": ROOT / "Cienaga/GEB - CIENAGA - AUTOICA Y RETEICA - NOVIEMBRE - 2025 .pdf",
        "thomson": [ROOT / "Cienaga/11_25 GEBH CIENEGA THOMSON AutoICA.xlsx", ROOT / "Cienaga/11_25 GEBH CIENEGA THOMSON ReteICA.xlsx"],
        "checklist": ROOT / "Cienaga/Cienaga - Check List Validación Calidad Auto y Rete.xlsx",
    },
}


def municipalities(): return ["Ciénaga", "Maicao", "Soacha"]
def declaration_types(municipality: str):
    values = [kind for (mun, kind) in CASES if mun == municipality]
    return values or ["Pendiente de mapeo"]
