# Validador Inteligente de Declaraciones Tributarias GEB

POC web para revisar declaraciones municipales ICA, AutoICA y ReteICA. Conserva la validación determinística de casos mapeados y añade una carga manual asistida por Gemini.

## Estructura

El código vive en esta carpeta `codigo/`. Los documentos tributarios de Ciénaga, Maicao, Soacha y los consolidados permanecen en la carpeta superior y no se duplican.

## Instalación en Windows

Desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configurar Gemini

Crea un archivo `.env` en esta carpeta, junto a `app.py`:

```dotenv
GEMINI_API_KEY=PEGAR_AQUI_LA_API_KEY_NUEVA
```

Opcionalmente se puede elegir otro modelo o límite por fuente:

```dotenv
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_SOURCE_CHARS=120000
```

`.env` está excluido en `.gitignore`: nunca debe confirmarse ni compartirse en el repositorio.

## Ejecutar Streamlit

```powershell
streamlit run app.py
```

La interfaz estará normalmente en `http://localhost:8501`.

## Ejecutar FastAPI

```powershell
uvicorn api:app --reload
```

La documentación interactiva estará en `http://localhost:8000/docs`.

## Modos disponibles

### Demo mapeada

Usa `case_registry.py`, los parsers locales y `validation_engine.py`. Las comparaciones de NIT, nombres, períodos y dinero se realizan con reglas determinísticas. Ciénaga está mapeada; los demás municipios se muestran como pendientes para evitar resultados sin evidencia.

### Carga manual con Gemini

Permite cargar:

- Checklist, declaración y Thomson: obligatorios.
- Consolidado de ingresos y retenciones: opcionales.
- Formatos: `.xlsx`, `.xlsm`, `.pdf`, `.md`, `.txt` y `.csv`.

La aplicación extrae internamente el texto, construye el prompt de auditoría y solicita a Gemini una respuesta JSON. No existe un campo de prompt para el usuario. Antes de mostrarla, la respuesta se valida y los totales se recalculan desde el detalle.

Si una fuente supera el límite configurado, se conserva el inicio y el final, y se muestra una advertencia. Si Gemini devuelve JSON inválido, la interfaz muestra la respuesta cruda dentro de un expander de depuración.

## Resultado

Ambos modos muestran:

- Totales de `cumple`, `no_cumple` y `no_verificable`.
- Tabla filtrable con renglón, valores, fuente, explicación y evidencia.
- Descarga del resultado completo como JSON.

## Pruebas

```powershell
python -m pytest -q
```

