# Sesión 0 · Repaso previo (IA y Python)

Todo se ejecuta desde la **raíz del repositorio** con `uv run`. Los notebooks van **numerados en el orden de trabajo**:

1. **Configurar:** `bash instalar.sh` (o `instalar.ps1`), o [`01_configurar.ipynb`](01_configurar.ipynb). Te guía para elegir ruta de modelo y guardar tu clave en `.env`.
2. **Repasar:** [`02_repaso.ipynb`](02_repaso.ipynb), seis ejercicios cortos (IA y Python), sin red.
3. **Ejercicios:** [`03_ejercicios.ipynb`](03_ejercicios.ipynb), doce ejercicios con autocorrección, sin red.
4. **Pydantic AI con Gemini:** [`04_pydantic_ai_gemini.ipynb`](04_pydantic_ai_gemini.ipynb), con tu clave gratuita.

Ábrelos en VS Code (kernel `.venv`, ver el README principal) .

## Notebook 03 · Ejercicios

Doce ejercicios con autocorrección (✅/⏳) en tres partes: **A** IA con código (tokens y costo, temperatura, tipos de IA, ventana de contexto), **B** Python (comprensiones, `dataclass`, errores, JSON y despachador con lista blanca, choques de horario, `asyncio.gather`) y **C** Pydantic (validación y esquema de una tool). Todo funciona **sin red**.

## Notebook 04 · Pydantic AI con tu clave de Gemini

Cinco ejercicios (comprobar la configuración, crear el agente, errores amables, una respuesta real y comparar dos modelos) más un reto opcional (del texto libre a un `Gasto`). Necesita una clave gratuita de Gemini (sin tarjeta, en https://aistudio.google.com/apikey): tu `.env` debe tener `GEMINI_API_KEY` y `COURSE_OFFLINE=0` (y reiniciar el kernel). `uv run copiloto-configurar --ruta gemini` lo deja listo.

- Usa solo datos ficticios y **no imprimas ni subas tu clave**.
- **Entrega:** *Restart and Run All*, guarda cada notebook con las salidas (en VS Code: **Restart** y luego **Run All**) y muestra los ✅ al inicio de la sesión 1.
