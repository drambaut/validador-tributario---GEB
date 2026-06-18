from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CASES = {
    ("Ciénaga", "ICA anual"): {
        "pdf": ROOT / "Cienaga/GEB-CIENAGA-ICA-2025.pdf",
        "thomson": [ROOT / "Cienaga/GEB-CIENAGA-ICA-2025.xlsm"],
        "checklist": ROOT / "Cienaga/Cienaga-CheckListValidaciónCalidadICA.xlsx",
    },
    ("Ciénaga", "AutoICA + ReteICA mensual"): {
        "pdf": ROOT / "Cienaga/GEB-CIENAGA-AUTOICAYRETEICA-NOVIEMBRE-2025.pdf",
        "thomson": [ROOT / "Cienaga/11_25GEBHCIENEGATHOMSONAutoICA.xlsx", ROOT / "Cienaga/11_25GEBHCIENEGATHOMSONReteICA.xlsx"],
        "checklist": ROOT / "Cienaga/Cienaga-CheckListValidaciónCalidadAutoyRete.xlsx",
    },
}


def municipalities(): return ["Ciénaga", "Maicao", "Soacha"]
def declaration_types(municipality: str):
    values = [kind for (mun, kind) in CASES if mun == municipality]
    return values or ["Pendiente de mapeo"]
