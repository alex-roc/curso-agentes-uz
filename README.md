# Materiales para estudiantes


## Calendario

Virtual sincrónico, **lunes, miércoles y jueves de 19:00 a 22:00**, del 19 al 29 de octubre de 2026.

| Sesión | Fecha | Tema | Qué hay aquí |
|---|---|---|---|
| 0 | lun 19 oct (inicio) | Repaso previo: IA y Python | [`s0/`](s0/): notebooks numerados en orden: [`01_configurar`](s0/01_configurar.ipynb), [`02_repaso`](s0/02_repaso.ipynb), **tarea** [`03_ejercicios`](s0/03_ejercicios.ipynb) y [`04_pydantic_ai_gemini`](s0/04_pydantic_ai_gemini.ipynb) |
| 1 | mié 21 oct | De los chatbots a los agentes; herramientas, APIs y acciones | [`s1/`](s1/): notebook 01, bucle sin framework, terminal de chat (hoy se amplía con la parte de herramientas) |
| 2 | jue 22 oct | Conocimiento, contexto y memoria | próximamente |
| 3 | lun 26 oct | Interoperabilidad, automatización y MCP | próximamente |
| 4 | mié 28 oct | Flujos agénticos y sistemas de varios agentes | próximamente |
| 5 | jue 29 oct | Despliegue y cierre con el proyecto final | próximamente |

## Tarea de la S0: notebooks `s0/01` a `s0/04`

Orden recomendado: **configurar** (`bash instalar.sh` o [`01_configurar`](s0/01_configurar.ipynb)) → **repaso** ([`02_repaso`](s0/02_repaso.ipynb)) → **ejercicios** ([`03_ejercicios`](s0/03_ejercicios.ipynb): 12 con autocorrección ✅/⏳, IA con código, Python para agentes y Pydantic) → **Pydantic AI con Gemini** ([`04_pydantic_ai_gemini`](s0/04_pydantic_ai_gemini.ipynb): conecta tu propia clave gratuita, [cómo crearla](docs/gemini.md)). Los ✅ son la evidencia; se revisa al inicio de la sesión 1. Detalles en [`s0/README.md`](s0/README.md).

## Instalación en 3 pasos

1. **Descarga el repositorio:** `git clone https://github.com/alex-roc/curso-agentes-uz.git` y entra a la carpeta, o pulsa *Code → Download ZIP* en GitHub y descomprímelo.
2. **Ejecuta el instalador** (instala `uv`, Python 3.12 y las dependencias, y te guía para elegir y probar tu modelo):
   - macOS, Linux o Git Bash en Windows: `bash instalar.sh`
   - PowerShell en Windows: `powershell -ExecutionPolicy Bypass -File instalar.ps1`
3. **Abre los notebooks en VS Code** (ver «Notebooks en VS Code», abajo).

El único requisito previo es tener internet. Si prefieres hacerlo por partes: `uv sync` y luego `uv run copiloto-configurar` (repítelo cuando quieras cambiar de ruta). Alternativa: [`s0/01_configurar.ipynb`](s0/01_configurar.ipynb). Detalles en la sección siguiente.

## Notebooks en VS Code

1. Instala [VS Code](https://code.visualstudio.com) y abre **la carpeta del repositorio** (Archivo → Abrir carpeta). Acepta instalar las extensiones recomendadas: **Python** y **Jupyter**. La carpeta trae `.vscode/settings.json`, que ya apunta al `.venv`.
2. Abre un notebook (por ejemplo `s0/03_ejercicios.ipynb`) y, arriba a la derecha, pulsa **Select Kernel → Python Environments → `.venv`** (el entorno que creó `instalar.sh`). Si no aparece, ejecuta antes `uv sync` y recarga la ventana.
3. Ejecuta celda por celda con **Shift+Enter**, o **Run All**. Si cambias `.env` (por ejemplo `COURSE_OFFLINE=0`), pulsa **Restart** en la barra del notebook.

## Instalar a mano

Si no usaste el instalador, necesitas [uv](https://docs.astral.sh/uv/) y Git. uv descarga su propio Python 3.12 sin tocar el de tu sistema.

```bash
git clone https://github.com/alex-roc/curso-agentes-uz.git
cd curso-agentes-uz
uv sync                  # crea .venv con las dependencias fijadas en uv.lock
uv run copiloto-configurar   # crea .env, elige tu ruta de modelo y la prueba (.env nunca se sube a Git)
code .                  # abre la carpeta en VS Code (o Archivo → Abrir carpeta)
```

- **macOS:** `brew install uv git`. **Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Windows:** usa **Git Bash** y sigue [docs/windows.md](docs/windows.md); los comandos son idénticos.
- Si un notebook usa otro Python, elige el kernel del `.venv` del repositorio.

## Las cuatro rutas de modelo

Los notebooks y scripts funcionan con cualquiera; cambia una línea de `.env` (`MODE`) y el resto es igual.

| Ruta | `MODE` | Qué necesitas | Guía |
|---|---|---|---|
| Ollama local | `local` | Ollama y ~2,5 GB de modelo; datos en tu equipo | [docs/ollama.md](docs/ollama.md) |
| Gemini gratis | `gemini` | Clave gratuita de AI Studio, sin tarjeta | [docs/gemini.md](docs/gemini.md) |
| OpenRouter `:free` | `openrouter` | Clave gratuita y un modelo que termine en `:free` | [docs/openrouter.md](docs/openrouter.md) |
| Simulado | `offline` | Nada (no es IA: solo muestra el recorrido) | este README |

Los notebooks arrancan con el modelo **simulado** (`COURSE_OFFLINE=1` en `.env`). Para IA real, pon `COURSE_OFFLINE=0` y **reinicia el kernel**. Comprueba tu ruta con `uv run copiloto-doctor --live`. `.env` tiene prioridad sobre las variables de tu terminal (p. ej. una `GEMINI_API_KEY` exportada), así lo que configuraste es lo que se usa.

> En las rutas gratuitas tus mensajes viajan a un proveedor y pueden usarse para mejorar sus productos: usa solo datos ficticios.

## Evaluación

- **Nota mínima de aprobación: 70/100.** Asistencia mínima: 80 %.
- **Trabajo final (100 % de la nota):** un **agente desplegado** más un **video explicativo subido a YouTube** (entrega el enlace). Fecha límite: **5 de noviembre de 2026**.

## Qué hay en el repositorio

```
instalar.sh / instalar.ps1   instalador de un paso (uv, dependencias, configurador)
copiloto/    módulo pequeño compartido: configuración, configurador, modelo simulado, agente básico
s0/          sesión 0: repaso y tarea de ejercicios (IA, Python, Pydantic, Gemini)
s1/          sesión 1: notebook de la tarea, bucle sin framework, terminal de chat
docs/        guías de instalación y de cada ruta de modelo
fuentes/     para quien mantiene el repo: fuentes .py de los notebooks y su generador
```

## Licencias

El **código** es [MIT](LICENSE); los **textos y notebooks** son [CC BY 4.0](LICENSE-MATERIALES.md): puedes reutilizarlos citando la autoría. Todos los datos de práctica son ficticios.

## Para quien mantiene el repositorio

Los notebooks se escriben en `fuentes/sN/*.py` (celdas con `# %%`) y se generan sin salidas con `python3 fuentes/generar_notebooks.py`. Edita siempre la fuente.
