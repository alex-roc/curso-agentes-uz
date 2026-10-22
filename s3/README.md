# Sesión 3 · Interoperabilidad, automatización y MCP

Lunes 26 de octubre de 2026. Conectas tu agente con otras aplicaciones mediante **MCP** (*Model Context Protocol*): usas un servidor que escribió otra persona, creas el tuyo, cuidas sus **contratos**, **errores** y **permisos**, pones al agente a trabajar **sin persona** y lo defiendes de la **inyección indirecta**.

**Antes de empezar:** `git pull` y `uv sync` (entra el SDK de MCP). Los servidores de terceros se descargan con `uvx`, que viene con `uv`.

## Cómo se conecta con la clase

En clase hay cinco demos (**Demo 1** a **Demo 5**). El notebook alterna un **ejemplo mínimo** (el código de la demo) con un **ejercicio** que lo varía.

| Ejercicio | Qué haces | Se apoya en | Nivel |
|---|---|---|---|
| 1 · Otro servidor | conectar `mcp-server-fetch` y leer una página | Demo 1 · Servidor ya hecho | básico |
| 2 · Tu primera tool MCP | `buscar_libros` en tu servidor `biblioteca` | Demo 2 · Tu servidor | básico |
| 3 · Un error que ayuda | `libros_entre` con `ToolError` | Demo 3 · Contratos y errores | medio |
| 4 · Mínimo privilegio | `allowed_tools`: el agente no ve `prestar_libro` | Demo 3 · Permisos | básico |
| 5 · El informe del día | `informe_diario()` guarda un archivo con la fecha | Demo 4 · Automatización | medio |
| 6 · Marcar lo externo | `como_dato`: lo leído es dato, no órdenes | Demo 5 · Inyección indirecta | medio |
| Reto · Tu servidor aparte | `mi_servidor.py` lanzado por stdio | Demo 2 | reto |

## Cómo trabajar

1. Abre la carpeta del repo en VS Code, abre `s3/01_mcp_e_integracion.ipynb`, elige el kernel `.venv` y ejecuta con Shift+Enter.
2. Cada ejercicio tiene `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.

- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. **No es IA**: elige tools por parecido de palabras.
- **IA real:** `COURSE_OFFLINE=0` en `.env` y *Restart* del kernel.
- En el notebook tu servidor corre **en memoria** (`MCP(local=biblioteca)`): mismo protocolo, sin un proceso aparte. En la demo y en el reto corre como archivo `.py` por stdio.
- El notebook crea `informes/` (y `mi_servidor.py` si haces el reto) en esta carpeta.
- **Entrega** (se revisa al inicio de la siguiente sesión): tu notebook con los ejercicios y, si puedes, las salidas de una ejecución con IA real.
