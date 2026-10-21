# Sesión 1 · De los chatbots a los agentes, herramientas, APIs y acciones

Miércoles 21 de octubre de 2026 (la S0 fue el lunes 19). Esta sesión fusiona «de los chatbots a los agentes» con «herramientas, APIs y acciones»: **los materiales de la S1 se actualizarán hoy con la parte de herramientas**; lo que hay ahora es la primera parte. Todo lo de esta carpeta se ejecuta desde la **raíz del repositorio** con `uv run`. Si aún no instalaste, sigue la [«Instalación en 3 pasos» del README](../README.md#instalación-en-3-pasos): `bash instalar.sh` (o `instalar.ps1`) lo deja todo listo y configura tu modelo.

## Qué hacer hoy, en orden

1. **Elige tu ruta de modelo** (5 a 15 min). Cualquiera sirve; sin ninguna, usa el simulado.
   - Gemini gratis: [../docs/gemini.md](../docs/gemini.md) (la más rápida) · OpenRouter: [../docs/openrouter.md](../docs/openrouter.md) · Ollama: [../docs/ollama.md](../docs/ollama.md).
   - Lo más fácil: `uv run copiloto-configurar` (te guía, guarda `.env` y prueba el modelo). Comprobar después: `uv run copiloto-doctor --live`.
2. **Mira el bucle de un agente sin framework:** `uv run python s1/bucle_sin_framework.py`. Un solo bucle, dos «modelos»: uno de juguete y un LLM real. Lee el código: son unas 60 líneas.
3. **Conversa con un agente en la terminal:** `uv run python s1/chat_terminal.py` (añade `--offline` para el modelo simulado). Pregúntale «¿qué hora es?» y «calcula el presupuesto de 3 horas a 40 Bs por hora»: verás cada tool que decide usar.
4. **La tarea: el notebook [`01_primer_agente.ipynb`](01_primer_agente.ipynb).** Cinco ejercicios con autocorrección y un reto. Hazlo primero con el simulado para entender el recorrido y después con IA real.
5. **Si te falta repaso,** [`../s0/02_repaso.ipynb`](../s0/02_repaso.ipynb).

## La tarea: `01_primer_agente.ipynb`

Ábrelo en VS Code con la carpeta del repositorio abierta: *Select Kernel → Python Environments → `.venv`*, y ejecuta con **Shift+Enter** o **Run All**.

- Cada ejercicio tiene una celda `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.
- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. Sirve para ver el ciclo y comprobar tu código; **no mide calidad**.
- **IA real:** pon `COURSE_OFFLINE=0` en `.env` y pulsa **Restart** en la barra del notebook. El ejercicio 5 (reto) solo tiene sentido así.
- `.env` gana sobre las variables de tu terminal: si exportas otra `GEMINI_API_KEY`, el curso usa la de `.env`.
- **Entrega:** el notebook con tus cambios y, si puedes, con las salidas de una ejecución con IA real. Guarda la tabla del ejercicio 5 y una frase sobre lo que la validación del esquema **no** puede comprobar.

## La terminal de chat (`chat_terminal.py`)

Una terminal pensada para ver al agente trabajar, más cómoda que la mínima de Pydantic AI (`agente.to_cli_sync()`, una línea, útil para una prueba rápida):

- respuesta en **Markdown**, dibujada a medida que llega (streaming) con los modelos reales;
- cada **tool** que el agente decide usar, con sus argumentos y su resultado, en tenue;
- **uso por turno** (requests y tokens) y **historial** entre turnos;
- errores amables (429, clave rechazada, Ollama apagado) sin traceback;
- Ctrl+C o Ctrl+D salen limpio.

| Comando | Qué hace |
|---|---|
| `/ayuda` | lista de comandos |
| `/modelo` | muestra la ruta y el modelo activos |
| `/uso` | requests y tokens acumulados de la sesión |
| `/mensajes` | recorrido del último turno: pedido, tools, respuesta |
| `/borrar` | olvida la conversación |
| `/salir` | termina |

Tiene dos tools de ejemplo (`calcular_presupuesto` y `hora_actual`, hora de La Paz). Añade las tuyas: son funciones con tipos y docstring, y se pasan en `tools=[...]`.

## Archivos

| Archivo | Qué es |
|---|---|
| `01_primer_agente.ipynb` | la tarea |
| `bucle_sin_framework.py` | el bucle de un agente con una interfaz de modelo (juguete o LLM real por HTTP) |
| `chat_terminal.py` | terminal de chat con tools, Markdown y streaming |
| `../copiloto/` | módulo compartido: `config.py` (rutas de modelo), `simulado.py`, `agente.py`, `practica.py` |

## Problemas frecuentes

| Síntoma | Qué hacer |
|---|---|
| El notebook dice «simulado» y quiero IA real | `COURSE_OFFLINE=0` en `.env` y reinicia el kernel |
| `ConnectError` o «conexión rechazada» | Ollama no está activo ([ollama.md](../docs/ollama.md)) |
| `429` | Cuota gratuita agotada: espera, cambia `GEMINI_MODEL` o usa otra ruta |
| 401 o 403 | Clave mal copiada: revisa `.env` |
| `ModuleNotFoundError: copiloto` | Estás con otro Python: usa `uv run` o el kernel del `.venv` |
