# Sesión 1 · De los chatbots a los agentes de IA, con herramientas y acciones

Miércoles 21 de octubre de 2026. Programas tu agente con **Pydantic AI directamente**: no hay ninguna capa intermedia. Los notebooks se ejecutan desde VS Code; los scripts, con `uv run` desde la carpeta `s1/`. Si aún no instalaste, sigue la [«Instalación en 3 pasos» del README](../README.md). Si ya clonaste el repo, `git pull` te trae esta carpeta.

## Cómo se conecta con la clase

La clase tiene tres actos; en cada uno el docente muestra una idea y la hace en vivo, y tú la repites en tu notebook.

| Acto | Qué se ve en clase | Lo repites en |
|---|---|---|
| Arranque | caso Mi copiloto, rutas de modelo, utilidades | paso 1 de abajo: `python -m utilidades.configurar` |
| 1 · ¿Qué es un agente? | chatbot, flujo y agente; anatomía; el bucle ReAct | `bucle_sin_framework.py` y notebook 01, secciones 2 a 2.1 |
| 2 · Lo mismo con Pydantic AI | frameworks, elegir modelo, salida estructurada, errores | notebook 01, secciones 2.2 a 7, y ejercicios 1 y 2 |
| 3 · Darle manos: herramientas | usar, preguntar o negarse; tools, `Deps`, `ModelRetry`; leer frente a escribir | notebook 02, secciones 1 a 5, y ejercicios 3 a 6 |
| Cierre | `mi_copiloto/agente.py` y la terminal | tu `s1/mi_copiloto/` (dos `# TODO`) y `python -m mi_copiloto.chat` |

Tu `mi_copiloto/agente.py` es el que el docente arma en vivo al final de la clase.

## Qué hacer, en orden

1. **Elige tu ruta de modelo** (5 a 15 min; cualquiera sirve, y sin ninguna usas el simulado): `uv run python -m utilidades.configurar` y luego `uv run python -m utilidades.doctor --live`. Guías: [Gemini](../docs/gemini.md) (la más rápida), [OpenRouter](../docs/openrouter.md), [Ollama](../docs/ollama.md) con `gemma4:e2b`.
2. **Mira el bucle de un agente sin framework:** `cd s1` y `uv run python bucle_sin_framework.py` (añade `--sin-llm` para no usar red).
3. **[`01_primer_agente.ipynb`](01_primer_agente.ipynb)** (~20 min): el bucle, el primer agente con Pydantic AI y salida tipada. Ejercicios 1 (`PlanDia`) y 2 (despachador seguro).
4. **[`02_herramientas.ipynb`](02_herramientas.ipynb)** (~40 min): tools, `ModelRetry`, una API pública y aprobación. Ejercicios 3 (`minutos_libres`), 4 (rediseñar una tool), 5 (`ModelRetry`) y 6 (sin permiso no hay acción). Al final completas tu `mi_copiloto/agente.py`.
5. **Conversa con tu agente:** desde `s1/`, `uv run python -m mi_copiloto.chat` (añade `--simulado` si no tienes modelo y `--modo gemini` para elegir ruta). Pide «¿Qué tengo el 2030-05-14?» y «Agenda “Llamada con Ana” el 2030-05-16 de 15:00 a 16:00»: la acción espera tu `[s/N]`. `/borrar` y `/salir` funcionan dentro.
6. **Opcional, con IA real: [`03_ia_real.ipynb`](03_ia_real.ipynb)** (~20 min): usar una tool, preguntar o negarse, y el reto de comparar dos modelos.

Abre la carpeta del repo en VS Code (extensiones Python y Jupyter), abre `s1/01_primer_agente.ipynb`, elige el kernel `.venv` (*Select Kernel → Python Environments*) y ejecuta con Shift+Enter o *Run All*.

- Cada ejercicio tiene una celda `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.
- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. Sirve para ver el recorrido y comprobar tu código; **no es IA ni mide calidad** (elige tools por parecido de palabras y puede equivocarse con las fechas). Los notebooks 01 y 02 se pueden hacer enteros así.
- **IA real:** pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel (*Restart* en la barra del notebook). El notebook 03 solo tiene sentido así. Un modelo local pequeño (`gemma4:e2b`) a veces no llama bien una tool: es una limitación del modelo, no un error tuyo; Gemini gratis es la alternativa.
- **Entrega** (se revisa al inicio de la siguiente sesión): tus notebooks con los cambios, tu carpeta `s1/mi_copiloto/` completada y, si puedes, las salidas de una ejecución con IA real.

## Archivos

| Archivo | Qué es |
|---|---|
| `01_primer_agente.ipynb` | el bucle y el primer agente (ejercicios 1 y 2) |
| `02_herramientas.ipynb` | herramientas y aprobación (ejercicios 3 a 6) |
| `03_ia_real.ipynb` | opcional, con IA real: decidir y comparar modelos |
| `mi_copiloto/agente.py` | tu agente: `Respuesta`, instrucciones, `Deps`, tools y `crear_agente`. Tiene dos `# TODO` que completas con el notebook 02 |
| `mi_copiloto/chat.py` | la terminal: historial, trazas de tools y `[s/N]` para aprobar |
| `mi_copiloto/datos/` | agenda, correo y clima de práctica (ficticios o respuestas congeladas) |
| `bucle_sin_framework.py` | el bucle de un agente con una interfaz de modelo (juguete o LLM real por HTTP) |

## Problemas frecuentes

| Síntoma | Qué hacer |
|---|---|
| El notebook dice «simulado» y quiero IA real | `COURSE_OFFLINE=0` en `.env` y reinicia el kernel |
| `ModuleNotFoundError: mi_copiloto` | Abre el notebook desde su carpeta (`s1/`) con el kernel del `.venv`; en la terminal, haz `cd s1` primero |
| `NotImplementedError: Completa crear_evento` | Te falta un `# TODO` de `mi_copiloto/agente.py` (notebook 02, sección 5) |
| `ConnectError` o «conexión rechazada» | Ollama no está activo ([ollama.md](../docs/ollama.md)) |
| `429` | Cuota gratuita agotada: espera un minuto, cambia `GEMINI_MODEL` o usa otra ruta |
| 401 o 403 | Clave mal copiada: revisa `.env` |
| El modelo no propone el evento | Un modelo pequeño a veces responde sin llamar la tool: repite el pedido o prueba Gemini |
