from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from case_registry import CASES, declaration_types, municipalities
from gemini_client import GeminiConfigurationError, GeminiResponseError, validate_with_gemini
from validation_engine import validate_case

app = FastAPI(title="Validador Tributario GEB", version="0.2.0")


class ManualValidationRequest(BaseModel):
    checklist_text: str
    pdf_text: str
    thomson_text: str
    ingresos_text: str | None = None
    retenciones_text: str | None = None
    declaration_type: str | None = None


@app.get("/health")
def health(): return {"status": "ok"}


@app.get("/cases")
def cases(): return {m: declaration_types(m) for m in municipalities()}


@app.post("/validate")
def validate(municipality: str, declaration_type: str):
    config = CASES.get((municipality, declaration_type))
    if not config: raise HTTPException(404, "Caso pendiente de mapeo")
    return validate_case(config)


@app.post("/validate/manual")
def validate_manual(request: ManualValidationRequest):
    try:
        return validate_with_gemini(**request.model_dump())
    except GeminiConfigurationError as exc:
        raise HTTPException(503, str(exc)) from exc
    except GeminiResponseError as exc:
        raise HTTPException(502, {"message": str(exc), "raw_response": exc.raw_response}) from exc
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc

