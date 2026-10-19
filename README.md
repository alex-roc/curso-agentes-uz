# Más allá de los chatbots: materiales para estudiantes

Repositorio de apoyo del curso **«Más allá de los chatbots: desarrollo de agentes con inteligencia artificial»** (UNIFRANZ Formación Continua) de **Alex Ojeda Copa** · [Lab TecnoSocial](https://labtecnosocial.org).

No es el paquete completo del curso: son **piezas útiles para cada sesión**, que se publican a medida que avanzamos. El hilo conductor es **Mi copiloto**, el asistente personal (ficticio) de Alex: un agente que empezamos como un chat y terminamos desplegado.

## Calendario

Virtual sincrónico, **lunes, miércoles y jueves de 19:00 a 22:00**, del 19 al 29 de octubre de 2026.

| Sesión | Fecha | Tema | Qué hay aquí |
|---|---|---|---|
| 0 | antes del curso | Repaso previo: IA y Python | [`s0/00_repaso.ipynb`](s0/00_repaso.ipynb) |
| 1 | lun 19 oct | De los chatbots a los agentes de IA | [`s1/`](s1/): notebook 01 (la tarea), bucle sin framework, terminal de chat |
| 2 | mié 21 oct | Diseño de agentes, herramientas y acciones | próximamente |
| 3 | jue 22 oct | Conocimiento, contexto y memoria | próximamente |
| 4 | lun 26 oct | Interoperabilidad, automatización y MCP | próximamente |
| 5 | mié 28 oct | Flujos agénticos y sistemas de varios pasos | próximamente |
| 6 | jue 29 oct | Despliegue y proyecto final | próximamente |

## Tarea de la S1: `s1/01_primer_agente.ipynb`

**Es lo más importante de esta semana.** El notebook [`s1/01_primer_agente.ipynb`](s1/01_primer_agente.ipynb) tiene cinco ejercicios con autocorrección (✅/⏳) y un reto: escribir instrucciones, definir tu propio `output_type`, un despachador de tools robusto, medir el uso y comparar dos modelos. Funciona **sin red** con el modelo simulado y mejora mucho con IA real. Instrucciones en [`s1/README.md`](s1/README.md).

## Instalación en 3 pasos

1. **Descarga el repositorio:** `git clone https://github.com/alex-roc/curso-agentes-uz.git` y entra a la carpeta, o pulsa *Code → Download ZIP* en GitHub y descomprímelo.
2. **Ejecuta el instalador** (instala `uv`, Python 3.12 y las dependencias, y te guía para elegir y probar tu modelo):
   - macOS, Linux o Git Bash en Windows: `bash instalar.sh`
   - PowerShell en Windows: `powershell -ExecutionPolicy Bypass -File instalar.ps1`
3. **Abre los notebooks:** `uv run jupyter lab`

El único requisito previo es tener internet. Si prefieres hacerlo por partes: `uv sync` y luego `uv run copiloto-configurar` (repítelo cuando quieras cambiar de ruta). Alternativa en Jupyter: [`s0/configurar_y_probar.ipynb`](s0/configurar_y_probar.ipynb). Detalles en la sección siguiente.

## Instalar a mano

Si no usaste el instalador, necesitas [uv](https://docs.astral.sh/uv/) y Git. uv descarga su propio Python 3.12 sin tocar el de tu sistema.

```bash
git clone https://github.com/alex-roc/curso-agentes-uz.git
cd curso-agentes-uz
uv sync                  # crea .venv con las dependencias fijadas en uv.lock
uv run copiloto-configurar   # crea .env, elige tu ruta de modelo y la prueba (.env nunca se sube a Git)
uv run jupyter lab       # abre los notebooks
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
- **Trabajo final:** un **agente desplegado** más un **video explicativo subido a YouTube** (entrega el enlace). Fecha límite: **5 de noviembre de 2026**.

## Qué hay en el repositorio

```
instalar.sh / instalar.ps1   instalador de un paso (uv, dependencias, configurador)
copiloto/    módulo pequeño compartido: configuración, configurador, modelo simulado, agente básico
s0/          sesión 0: repaso (IA y Python)
s1/          sesión 1: notebook de la tarea, bucle sin framework, terminal de chat
docs/        guías de instalación y de cada ruta de modelo
fuentes/     para quien mantiene el repo: fuentes .py de los notebooks y su generador
```

## Licencias

El **código** es [MIT](LICENSE); los **textos y notebooks** son [CC BY 4.0](LICENSE-MATERIALES.md): puedes reutilizarlos citando la autoría. Todos los datos de práctica son ficticios.

## Para quien mantiene el repositorio

Los notebooks se escriben en `fuentes/sN/*.py` (celdas con `# %%`) y se generan sin salidas con `python3 fuentes/generar_notebooks.py`. Edita siempre la fuente.
