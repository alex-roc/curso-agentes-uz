# Sesión 1 · De los chatbots a los agentes de IA, con herramientas y acciones

Miércoles 21 de octubre de 2026. Programas tu agente con **Pydantic AI directamente**: no hay ninguna capa intermedia. Los notebooks se ejecutan desde VS Code; los scripts, con `uv run` desde la carpeta `s1/`. Si aún no instalaste, sigue la [«Instalación en 3 pasos» del README](../README.md). Si ya clonaste el repo, `git pull` te trae esta carpeta.

## Cómo se conecta con la clase

En clase hay cuatro demos numeradas (**Demo 1** a **Demo 4**) y luego unos 60 minutos de **Ejercicios 1 a 5** (más un reto opcional con IA real). Cada notebook empieza con «ejemplos mínimos», el mismo código de la demo explicado paso a paso; los ejercicios no lo repiten: cada uno es una variación (otro dato, otra tool, rechazar además de aprobar) y dice en qué demo se apoya.

| Ejercicio | Dónde | Se apoya en | Nivel |
|---|---|---|---|
| 1 · Extrae una tarea (`Tarea` con `Literal`) | `01_primer_agente` | Demo 1 · Salida tipada | básico |
| 2 · Tu primera tool (`minutos_entre`) | `02_herramientas` | Demo 2 · Primera tool | básico |
| 3 · Una tool que lee datos (`buscar_correos` con `deps`) | `02_herramientas` | Demo 3 · Tool con datos | medio |
| 4 · Sin permiso no hay acción (rechazar y aprobar) | `02_herramientas` | Demo 4 · Escribir con permiso | medio |
| 5 · Completa tu copiloto | `mi_copiloto/agente.py` (se comprueba al final del 02) | Demo 4 | básico |
| Reto · La misma pregunta, dos modelos | `03_ia_real` (IA real, opcional) | Demo 2 | reto |

## Qué hacer, en orden

1. **Elige tu ruta de modelo** (cualquiera sirve, y sin ninguna usas el simulado): `uv run python -m utilidades.configurar` y luego `uv run python -m utilidades.doctor --live`. Guías: [Gemini](../docs/gemini.md) (la más rápida) u [Ollama](../docs/ollama.md) con `gemma4:e2b`.
2. **[`01_primer_agente.ipynb`](01_primer_agente.ipynb)** (~15 min): un agente de texto y uno que extrae datos con `output_type`. Ejercicio 1.
3. **[`02_herramientas.ipynb`](02_herramientas.ipynb)** (~45 min): `tool_plain`, `deps` con `RunContext` y escrituras con aprobación. Ejercicios 2 a 4, y el 5: completar tu `mi_copiloto/agente.py`.
4. **Conversa con tu agente:** desde `s1/`, `uv run python -m mi_copiloto.chat` (añade `--simulado` si no tienes modelo y `--modo gemini` para elegir ruta). Pide «¿Qué tengo el 2030-05-14?» y «Crea “Llamada con Ana” el 2030-05-16 de 15:00 a 16:00»: la acción espera tu `[s/N]`. `/borrar` y `/salir` funcionan dentro.
5. **Opcional, con IA real: [`03_ia_real.ipynb`](03_ia_real.ipynb)** (~15 min): el reto de comparar Gemini y `gemma4:e2b`.

Abre la carpeta del repo en VS Code (extensiones Python y Jupyter), abre `s1/01_primer_agente.ipynb`, elige el kernel `.venv` (*Select Kernel → Python Environments*) y ejecuta con Shift+Enter o *Run All*.

- Cada ejercicio tiene una celda `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.
- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. Sirve para ver el recorrido y comprobar tu código; **no es IA ni mide calidad** (elige tools por parecido de palabras y puede equivocarse con las fechas). Los notebooks 01 y 02 se pueden hacer enteros así.
- **IA real:** pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel (*Restart* en la barra del notebook). El notebook 03 solo tiene sentido así. Un modelo local pequeño (`gemma4:e2b`) a veces no llama bien una tool: es una limitación del modelo, no un error tuyo; Gemini gratis es la alternativa.
- **Entrega** (se revisa al inicio de la siguiente sesión): tus notebooks con los cambios, tu carpeta `s1/mi_copiloto/` completada y, si puedes, las salidas de una ejecución con IA real.

## Archivos

| Archivo | Qué es |
|---|---|
| `01_primer_agente.ipynb` | el primer agente y la salida tipada (Ejercicio 1) |
| `02_herramientas.ipynb` | herramientas y aprobación (Ejercicios 2 a 5) |
| `03_ia_real.ipynb` | opcional, con IA real: el reto de dos modelos |
| `mi_copiloto/agente.py` | tu agente: `Respuesta`, instrucciones, `Deps`, tools y `crear_agente`. Tiene dos `# TODO Ejercicio 5` |
| `mi_copiloto/chat.py` | la terminal: historial, trazas de tools y `[s/N]` para aprobar |
| `mi_copiloto/datos/` | agenda, correo y clima de práctica (ficticios o respuestas congeladas) |

## Problemas frecuentes

| Síntoma | Qué hacer |
|---|---|
| El notebook dice «simulado» y quiero IA real | `COURSE_OFFLINE=0` en `.env` y reinicia el kernel |
| `ModuleNotFoundError: mi_copiloto` | Abre el notebook desde su carpeta (`s1/`) con el kernel del `.venv`; en la terminal, haz `cd s1` primero |
| `NotImplementedError: Completa crear_evento (Ejercicio 5)` | Te falta un `# TODO Ejercicio 5` de `mi_copiloto/agente.py` |
| `ConnectError` o «conexión rechazada» | Ollama no está activo ([ollama.md](../docs/ollama.md)) |
| `429` | Cuota gratuita agotada: espera un minuto, cambia `GEMINI_MODEL` o usa otra ruta |
| 401 o 403 | Clave mal copiada: revisa `.env` |
| El modelo no propone el evento | Un modelo pequeño a veces responde sin llamar la tool: repite el pedido o prueba Gemini |
