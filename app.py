from __future__ import annotations

import json
import os
import pandas as pd
import streamlit as st
from case_registry import CASES, declaration_types, municipalities
from file_reader import SUPPORTED_EXTENSIONS, read_uploaded_file
from gemini_client import GeminiConfigurationError, GeminiResponseError, validate_with_gemini
from validation_engine import validate_case

st.set_page_config(page_title="Validador tributario GEB", page_icon="✅", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1450px; padding-top: 2rem}
[data-testid="stMetric"] {background:#f6f8fb;border:1px solid #e3e8ef;border-radius:12px;padding:14px}
</style>""", unsafe_allow_html=True)
st.title("Validador inteligente de declaraciones")
st.caption("POC · Demo determinística y carga manual asistida por Gemini · Evidencia trazable")


def _display(value):
    if value is None or value == "": return "—"
    if isinstance(value, list): return ", ".join(map(str, value))
    return str(value)


def render_report(report: dict):
    summary = report["summary"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Validaciones", summary["total"]); c2.metric("Cumplen", summary["cumple"])
    c3.metric("No cumplen", summary["no_cumple"]); c4.metric("No verificables", summary["no_verificable"])

    meta = report.get("_meta", {})
    if meta.get("truncated_sources"):
        st.warning("Se recortó de forma controlada el texto de: " + ", ".join(meta["truncated_sources"]) + ". Revisa especialmente los resultados no verificables.")

    st.subheader("Detalle")
    states = ["cumple", "no_cumple", "no_verificable"]
    selected = st.multiselect("Filtrar estado", states, default=states)
    labels = {"cumple": "✅ Cumple", "no_cumple": "❌ No cumple", "no_verificable": "⚠️ No verificable"}
    rows = []
    for item in report["results"]:
        if item["status"] not in selected: continue
        rows.append({
            "#": item.get("number", ""), "Validación": item.get("validation", ""),
            "Renglón": item.get("renglon") or item.get("evidence", ""), "Estado": labels[item["status"]],
            "Encontrado en PDF": _display(item.get("found")), "Esperado / fuente verdad": _display(item.get("expected")),
            "Fuente": item.get("source", ""), "Explicación": item.get("explanation", ""),
            "Evidencia": item.get("evidence", ""),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch",
                 column_config={"Explicación": st.column_config.TextColumn(width="large"),
                                "Evidencia": st.column_config.TextColumn(width="large")})
    if report.get("documents"):
        with st.expander("Documentos utilizados"): st.json(report["documents"])
    st.download_button("Descargar evidencia JSON", json.dumps(report, ensure_ascii=False, indent=2, default=str),
                       "resultado_validacion.json", "application/json")


with st.sidebar:
    st.header("Modo de validación")
    mode = st.selectbox("Modo", ["Demo mapeada", "Carga manual con Gemini"])
    if mode == "Demo mapeada":
        municipality = st.selectbox("Municipio", municipalities())
        declaration_type = st.selectbox("Tipo de declaración", declaration_types(municipality))
        run_demo = st.button("Ejecutar validación", type="primary", width="stretch")
        st.caption("Thomson es la fuente esperada; el PDF contiene lo presentado y el checklist define qué revisar.")
    else:
        declaration_type = st.selectbox("Tipo de declaración", ["ICA anual", "AutoICA + ReteICA mensual", "Otro"])
        allowed = [ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)]
        checklist = st.file_uploader("Checklist *", type=allowed)
        declaration = st.file_uploader("PDF de declaración *", type=allowed)
        thomson = st.file_uploader("Archivo Thomson *", type=allowed)
        ingresos = st.file_uploader("Consolidado de ingresos (opcional)", type=allowed)
        retenciones = st.file_uploader("Consolidado de retenciones (opcional)", type=allowed)
        run_manual = st.button("Validar con Gemini", type="primary", width="stretch")
        st.caption("Los archivos cargados se envían a Gemini al pulsar el botón. No se solicita ni se almacena un prompt del usuario.")

if mode == "Demo mapeada" and run_demo:
    config = CASES.get((municipality, declaration_type))
    if not config:
        st.warning("Este caso aún no tiene un mapeo validado; no se generarán resultados aparentes sin evidencia.")
    else:
        with st.spinner("Leyendo documentos y ejecutando reglas determinísticas…"):
            st.session_state["report"] = validate_case(config)
            st.session_state["report_mode"] = mode

if mode == "Carga manual con Gemini" and run_manual:
    missing = [name for name, value in (("checklist", checklist), ("declaración", declaration), ("Thomson", thomson)) if value is None]
    if missing:
        st.warning("Faltan archivos obligatorios: " + ", ".join(missing) + ".")
    elif not os.getenv("GEMINI_API_KEY"):
        st.error("No existe GEMINI_API_KEY. Configúrala en codigo/.env y reinicia la aplicación.")
    else:
        try:
            with st.spinner("Extrayendo archivos y validando con Gemini…"):
                report = validate_with_gemini(
                    read_uploaded_file(checklist), read_uploaded_file(declaration), read_uploaded_file(thomson),
                    read_uploaded_file(ingresos) if ingresos else None,
                    read_uploaded_file(retenciones) if retenciones else None, declaration_type,
                )
                st.session_state["report"] = report
                st.session_state["report_mode"] = mode
        except GeminiResponseError as exc:
            st.error(str(exc))
            with st.expander("Respuesta cruda de Gemini para depuración"): st.code(exc.raw_response or "[Respuesta vacía]", language="text")
        except (GeminiConfigurationError, ValueError, RuntimeError) as exc:
            st.error(str(exc))

report = st.session_state.get("report")
if report and st.session_state.get("report_mode") == mode:
    render_report(report)
elif mode == "Demo mapeada":
    st.info("Selecciona un caso y ejecuta la validación. Ciénaga está configurada con datos reales.")
else:
    st.info("Carga los tres archivos obligatorios para iniciar la validación asistida por Gemini.")

