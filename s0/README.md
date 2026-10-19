# Sesión 0 · Repaso previo (IA y Python)

Todo se ejecuta desde la **raíz del repositorio** con `uv run`. Orden recomendado:

1. **Configurar:** `bash instalar.sh` (o `instalar.ps1`). Te guía para elegir ruta de modelo y guardar tu clave en `.env`.
2. **Repasar:** [`00_repaso.ipynb`](00_repaso.ipynb), seis ejercicios cortos (IA y Python), sin red.
3. **La tarea:** [`ejercicios_s0.ipynb`](ejercicios_s0.ipynb).

## Tarea de la S0: `ejercicios_s0.ipynb`

```bash
uv run jupyter lab s0/ejercicios_s0.ipynb
```

Trece ejercicios con autocorrección (✅/⏳) en cuatro partes: **A** IA con código (tokens y costo, temperatura, tipos de IA, ventana de contexto), **B** Python (comprensiones, `dataclass`, errores, JSON y despachador con lista blanca, choques de horario, `asyncio.gather`), **C** Pydantic (validación y esquema de una tool) y **D** conexión de Pydantic AI con **tu clave gratuita de Gemini** (sin tarjeta, en https://aistudio.google.com/apikey), más un reto opcional con IA real.

- Todo funciona **sin red**, salvo la parte D y el reto. Para esas, tu `.env` debe tener `GEMINI_API_KEY` y `COURSE_OFFLINE=0` (y reiniciar el kernel). `uv run copiloto-configurar --ruta gemini` lo deja listo.
- Usa solo datos ficticios y **no imprimas ni subas tu clave**.
- **Entrega:** *Restart and Run All*, guarda el notebook con las salidas y muestra los ✅ al inicio de la sesión 1.
