"""Mi copiloto: el asistente personal de Alex (datos ficticios), construido sesión a sesión.

Crece un módulo por sesión del curso:

- S1: `agente.py` (instrucciones, tools y aprobación) y `chat.py` (la terminal).
- Las demás sesiones añaden módulos nuevos aquí, uno por tema.

La IA se programa con Pydantic AI directamente: aquí no hay ninguna capa intermedia.
"""

import pydantic_ai

pydantic_ai.BANNER_ENABLED = False  # sin el aviso de Logfire al arrancar la terminal
