"""Utilidades del curso: infraestructura de apoyo, no contenido de IA.

La IA del curso se programa con Pydantic AI directamente (`Agent`, `@agent.tool`,
`output_type`…). Aquí solo viven las piezas que evitan repetir lo mismo en cada notebook:
elegir el modelo (`config`), un modelo simulado para practicar sin red (`simulado`),
ayudas de notebook (`practica`) y los comandos `doctor` y `configurar`.
"""

import pydantic_ai

pydantic_ai.BANNER_ENABLED = False  # sin el aviso de Logfire en cada notebook y cada script
