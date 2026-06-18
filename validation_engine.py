from collections import ChainMap
from pathlib import Path
from typing import Any
from checklist_parser import parse_checklist
from excel_parser import parse_thomson
from models import ValidationResult
from pdf_parser import parse_pdf
from text_utils import digits, money, names_equivalent, normalize_text


CONCEPT_FIELD = {
    "REPRESENTANTE LEGAL": "representante", "REVISOR FISCAL": "revisor",
    "RAZON SOCIAL": "razon_social", "IDENTIFICACION": "nit", "ANO GRAVABLE": "anio",
    "PERIODO GRAVABLE": "periodo", "DIRECCION": "direccion", "CIUDAD": "municipio",
    "DEPARTAMENTO": "departamento", "CIIU": "ciiu", "TELEFONO": "telefono",
    "CORREO": "email", "BASE GRAVABLE": "base_gravable", "IMPUESTO INDUSTRIA": "impuesto_ica",
    "INGRESOS TOTALES": "ingresos_totales", "INGRESOS FUERA": "ingresos_fuera",
    "INGRESOS DEL MUNICIPIO": "ingresos_municipio", "TARIFA": "tarifa",
    "AVISOS": "avisos_tableros", "BOMBERIL": "sobretasa_bomberil", "SEGURIDAD": "sobretasa_seguridad",
    "TOTAL DEL IMPUESTO": "total_impuesto_cargo", "VALOR A PAGAR EN LETRAS": "valor_letras",
    "VALOR A PAGAR": "valor_pagar", "AUTORRETENCIONES": "autorretenciones",
    "ANTICIPOS": "anticipos", "SALDOS A FAVOR": "saldo_favor",
}
MONEY_FIELDS = {"base_gravable", "impuesto_ica", "ingresos_totales", "ingresos_fuera", "ingresos_municipio",
                "avisos_tableros", "sobretasa_bomberil", "sobretasa_seguridad", "total_impuesto_cargo",
                "valor_pagar", "autorretenciones", "retenciones", "anticipos", "saldo_favor"}


def field_for(concept: str) -> str | None:
    normalized = normalize_text(concept)
    return next((field for token, field in CONCEPT_FIELD.items() if token in normalized), None)


def compare(field: str, found: Any, expected: Any) -> tuple[str, str, str]:
    if found in (None, "", []) or expected in (None, "", []):
        return "no_verificable", "No existe evidencia suficiente en ambas fuentes.", "presencia en PDF y Thomson"
    if field in MONEY_FIELDS:
        ok = money(found) == money(expected); rule = "igualdad exacta en pesos"
    elif field in {"nit", "telefono", "representante_id", "revisor_id"}:
        ok = digits(found) == digits(expected); rule = "igualdad de dígitos"
    elif field in {"razon_social", "representante", "revisor"}:
        ok = names_equivalent(found, expected); rule = "equivalencia de nombres normalizados"
    elif isinstance(found, list) or isinstance(expected, list):
        fa = {digits(x) for x in (found if isinstance(found, list) else [found])}
        ex = {digits(x) for x in (expected if isinstance(expected, list) else [expected])}
        ok = bool(fa & ex); rule = "intersección de códigos normalizados"
    else:
        left, right = normalize_text(found), normalize_text(expected)
        if field == "direccion":
            aliases = {"CRA":"CR", "CARRERA":"CR", "NO":"N", "NUMERO":"N", "PSO":"P", "PISO":"P"}
            left = " ".join(aliases.get(x, x) for x in left.split())
            right = " ".join(aliases.get(x, x) for x in right.split())
            ok = left in right or right in left
            rule = "equivalencia de dirección normalizada"
        else:
            ok = left == right; rule = "igualdad de texto normalizado"
    return ("cumple" if ok else "no_cumple", "Coincide entre PDF y Thomson." if ok else "Diferencia encontrada entre PDF y Thomson.", rule)


def validate_case(config: dict) -> dict:
    pdf = parse_pdf(Path(config["pdf"]))
    sources = [parse_thomson(Path(p)) for p in config["thomson"]]
    expected = dict(ChainMap(*sources))
    # En casos combinados, agrega campos exclusivos de las fuentes secundarias.
    for source in sources[1:]:
        for key, value in source.items():
            if expected.get(key) in (None, "", []): expected[key] = value
    if len(sources) > 1 and all(s.get("valor_pagar") is not None for s in sources):
        expected["valor_pagar"] = sum(money(s["valor_pagar"]) for s in sources)
    rules = parse_checklist(Path(config["checklist"]))
    results = []
    for item in rules:
        field = field_for(item.concept)
        found, wanted = (pdf.get(field), expected.get(field)) if field else (None, None)
        status, explanation, rule = compare(field or "", found, wanted)
        results.append(ValidationResult(item.number, item.concept, status, found, wanted,
            f"{Path(config['pdf']).name} ↔ {', '.join(Path(p).name for p in config['thomson'])}",
            explanation, item.reference, rule).to_dict())
    counts = {state: sum(r["status"] == state for r in results) for state in ("cumple", "no_cumple", "no_verificable")}
    return {"summary": {"total": len(results), **counts}, "results": results,
            "documents": {"pdf": Path(config["pdf"]).name, "thomson": [Path(p).name for p in config["thomson"]],
                          "checklist": Path(config["checklist"]).name}}
