# Sesión 1 · De los chatbots a los agentes de IA, con herramientas y acciones

Miércoles 21 de octubre de 2026. Programas tu agente con **Pydantic AI directamente**: no hay ninguna capa intermedia. Los notebooks se ejecutan desde VS Code; los scripts, con `uv run` desde la carpeta `s1/`. Si aún no instalaste, sigue la [«Instalación en 3 pasos» del README](../README.md). Si ya clonaste el repo, `git pull` te trae esta carpeta.

## Cómo se conecta con la clase

En clase hay cinco demos numeradas (**Demo 1** a **Demo 5**) y luego 60 minutos de **Ejercicios 1 a 9**. Los ejercicios no repiten la demo: cada uno cambia algo (otro dato, otra tool, un diseño malo que mejorar, algo que medir) y dice en qué demo se apoya.

| Ejercicio | Dónde | Se apoya en | Nivel |
|---|---|---|---|
| 1 · Tu propio `output_type`: `PlanDia` | `01_primer_agente` | Demo 3 | básico |
| 2 · Un despachador que sobrevive a los errores | `01_primer_agente` | Demo 2 | medio |
| 3 · Una función pura y una tool nueva | `02_herramientas` | Demo 4 | medio |
| 4 · Rediseña una tool mal hecha | `02_herramientas` | Demo 4 | medio |
| 5 · Un error que enseña: `ModelRetry` | `02_herramientas` | Demo 4 | básico |
| 6 · Sin permiso no hay acción | `02_herramientas` | Demo 5 | medio |
| 7 · Lleva tu agente a `mi_copiloto/` | `mi_copiloto/agente.py` (se comprueba al final del 02) | Demo 5 | básico |
| 8 · Tu regla: usar, preguntar o negarse | `03_ia_real` (IA real, opcional) | Demo 4 | medio |
| 9 · Reto: mismo pedido, dos modelos | `03_ia_real` (IA real, opcional) | Demos 1 y 3 | reto |

## Qué hacer, en orden

1. **Elige tu ruta de modelo** (5 a 15 min; cualquiera sirve, y sin ninguna usas el simulado): `uv run python -m utilidades.configurar` y luego `uv run python -m utilidades.doctor --live`. Guías: [Gemini](../docs/gemini.md) (la más rápida), [OpenRouter](../docs/openrouter.md), [Ollama](../docs/ollama.md) con `gemma4:e2b`.
2. **Mira el bucle de un agente sin framework:** `cd s1` y `uv run python bucle_sin_framework.py` (añade `--sin-llm` para no usar red).
3. **[`01_primer_agente.ipynb`](01_primer_agente.ipynb)** (~20 min): el bucle, el primer agente con Pydantic AI y salida tipada. Ejercicios 1 y 2.
4. **[`02_herramientas.ipynb`](02_herramientas.ipynb)** (~40 min): tools, `ModelRetry`, una API pública y aprobación. Ejercicios 3 a 6, y el 7: completar tu `mi_copiloto/agente.py`.
5. **Conversa con tu agente:** desde `s1/`, `uv run python -m mi_copiloto.chat` (añade `--simulado` si no tienes modelo y `--modo gemini` para elegir ruta). Pide «¿Qué tengo el 2030-05-14?» y «Agenda “Llamada con Ana” el 2030-05-16 de 15:00 a 16:00»: la acción espera tu `[s/N]`. `/borrar` y `/salir` funcionan dentro.
6. **Opcional, con IA real: [`03_ia_real.ipynb`](03_ia_real.ipynb)** (~20 min): Ejercicios 8 (usar, preguntar o negarse) y 9 (reto: comparar dos modelos).

Abre la carpeta del repo en VS Code (extensiones Python y Jupyter), abre `s1/01_primer_agente.ipynb`, elige el kernel `.venv` (*Select Kernel → Python Environments*) y ejecuta con Shift+Enter o *Run All*.

- Cada ejercicio tiene una celda `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.
- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. Sirve para ver el recorrido y comprobar tu código; **no es IA ni mide calidad** (elige tools por parecido de palabras y puede equivocarse con las fechas). Los notebooks 01 y 02 se pueden hacer enteros así.
- **IA real:** pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel (*Restart* en la barra del notebook). El notebook 03 solo tiene sentido así. Un modelo local pequeño (`gemma4:e2b`) a veces no llama bien una tool: es una limitación del modelo, no un error tuyo; Gemini gratis es la alternativa.
- **Entrega** (se revisa al inicio de la siguiente sesión): tus notebooks con los cambios, tu carpeta `s1/mi_copiloto/` completada y, si puedes, las salidas de una ejecución con IA real.

## Archivos

| Archivo | Qué es |
|---|---|
| `01_primer_agente.ipynb` | el bucle y el primer agente (Ejercicios 1 y 2) |
| `02_herramientas.ipynb` | herramientas y aprobación (Ejercicios 3 a 7) |
| `03_ia_real.ipynb` | opcional, con IA real: Ejercicios 8 y 9 |
| `mi_copiloto/agente.py` | tu agente: `Respuesta`, instrucciones, `Deps`, tools y `crear_agente`. Tiene dos `# TODO Ejercicio 7` |
| `mi_copiloto/chat.py` | la terminal: historial, trazas de tools y `[s/N]` para aprobar |
| `mi_copiloto/datos/` | agenda, correo y clima de práctica (ficticios o respuestas congeladas) |
| `bucle_sin_framework.py` | el bucle de un agente con una interfaz de modelo (juguete o LLM real por HTTP) |

## Problemas frecuentes

| Síntoma | Qué hacer |
|---|---|
| El notebook dice «simulado» y quiero IA real | `COURSE_OFFLINE=0` en `.env` y reinicia el kernel |
| `ModuleNotFoundError: mi_copiloto` | Abre el notebook desde su carpeta (`s1/`) con el kernel del `.venv`; en la terminal, haz `cd s1` primero |
| `NotImplementedError: Completa crear_evento (Ejercicio 7)` | Te falta un `# TODO Ejercicio 7` de `mi_copiloto/agente.py` |
| `ConnectError` o «conexión rechazada» | Ollama no está activo ([ollama.md](../docs/ollama.md)) |
| `429` | Cuota gratuita agotada: espera un minuto, cambia `GEMINI_MODEL` o usa otra ruta |
| 401 o 403 | Clave mal copiada: revisa `.env` |
| El modelo no propone el evento | Un modelo pequeño a veces responde sin llamar la tool: repite el pedido o prueba Gemini |
