# Sesión 1 · Introducción a Pydantic AI y tools

Miércoles 21 de octubre de 2026. Programas agentes con **Pydantic AI** directamente: un `Agent`, tools, `Capability`, salida tipada y tools que **leen** datos de APIs abiertas (sin clave) y de una base **SQLite** local, y una tool que **escribe** en esa base. Si aún no instalaste, sigue la [«Instalación en 3 pasos» del README](../README.md). Si ya clonaste el repo, `git pull` te trae esta carpeta.

## Cómo se conecta con la clase

En clase hay seis demos (**Demo 1** a **Demo 6**). El notebook alterna un **ejemplo mínimo** (el código de la demo) con un **ejercicio** que lo varía.

| Ejercicio | Qué haces | Se apoya en | Nivel |
|---|---|---|---|
| 1 · Extrae un libro | `output_type=Libro` (titulo, autor, anio) | Demo 1 · Agente y salida tipada | básico |
| 2 · Tu primera tool | `@vendedor.tool_plain precio_producto` | Demo 2 · Tool directa | básico |
| 3 · Capability de clima | `consultar_clima(ciudad)` con Open-Meteo | Demo 4 · API abierta | medio |
| 4 · Biblioteca en SQLite | `buscar_libros(texto)` de solo lectura | Demo 5 · SQLite | medio |
| 5 · Dos capabilities | un agente con `clima` y `biblioteca` | Demo 5 | medio |
| 6 · Registra libros | `registrar_libro` (una tool que **escribe** en SQLite) | Demo 6 · Escritura | medio |
| Reto · Tipo de cambio | `tipo_de_cambio` + `output_type`, y `defer_loading` | Demos 3 y 4 | reto |

## Cómo trabajar

1. **Elige tu ruta de modelo:** `uv run python -m utilidades.configurar` y luego `uv run python -m utilidades.doctor --live`. Guías: [Gemini](../docs/gemini.md) u [Ollama](../docs/ollama.md) con `gemma4:e2b`.
2. Abre la carpeta del repo en VS Code (extensiones Python y Jupyter), abre `s1/01_pydantic_ai_y_tools.ipynb`, elige el kernel `.venv` (*Select Kernel → Python Environments*) y ejecuta con Shift+Enter.
3. Cada ejercicio tiene `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.

- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. Sirve para ver el recorrido; **no es IA** (elige tools por parecido de palabras, y una sola por pregunta).
- **IA real:** `COURSE_OFFLINE=0` en `.env` y *Restart* del kernel. Las tools de clima, Banco Mundial y tipo de cambio necesitan internet.
- El notebook crea `proyectos.db` y `biblioteca.db` en esta carpeta: son datos ficticios de práctica.
- **Entrega** (se revisa al inicio de la siguiente sesión): tu notebook con los ejercicios y, si puedes, las salidas de una ejecución con IA real.
