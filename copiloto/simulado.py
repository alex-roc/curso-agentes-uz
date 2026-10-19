"""Modelo simulado para practicar sin LLM: elige una tool por palabras clave y resume.

NO es inteligencia artificial. Sirve para ver el ciclo completo (pedido → tool → resultado
→ respuesta tipada) cuando no hay modelo, red o cuota. Su texto empieza con «[simulado]».
"""

import json
import re

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel


def _presupuesto(texto: str) -> dict:
    nums = [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", texto)]
    return {"horas": nums[0] if nums else 2, "tarifa": nums[1] if len(nums) > 1 else 35}


# (patrón, herramienta, argumentos). Se usa la primera regla cuya tool exista en el agente.
# Cuando una sesión añada tools, se añade aquí su regla.
REGLAS = [
    (r"presupuesto|costo|tarifa", "calcular_presupuesto", _presupuesto),
    (r"hora|fecha|d[ií]a|hoy", "hora_actual", lambda t: {}),
]


def _ultimo_pedido(messages: list[ModelMessage]) -> str:
    for mensaje in reversed(messages):
        if isinstance(mensaje, ModelRequest):
            for parte in mensaje.parts:
                if isinstance(parte, UserPromptPart) and isinstance(parte.content, str):
                    return parte.content
    return ""


def _rellenar(schema: dict, defs: dict, texto: str, pedido: str):
    """Construye un objeto mínimo válido para el esquema de salida del agente."""
    if "$ref" in schema:
        return _rellenar(defs[schema["$ref"].split("/")[-1]], defs, texto, pedido)
    if "enum" in schema:
        return next((v for v in schema["enum"] if str(v) in pedido.lower()), schema["enum"][0])
    if "anyOf" in schema:
        return _rellenar(schema["anyOf"][0], defs, texto, pedido)
    tipo = schema.get("type")
    if tipo == "object":
        props = schema.get("properties", {})
        return {
            k: [] if k == "fuentes" else _rellenar(v, defs, texto, pedido)
            for k, v in props.items()
            if k in schema.get("required", []) or k in {"texto", "fuentes", "requiere_revision"}
        }
    if tipo == "array":
        item = schema.get("items", {})
        return [] if item.get("type") != "string" else [texto[:120]]
    if tipo == "boolean":
        return False
    if tipo in {"integer", "number"}:
        return 0
    return texto


def responder(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    pedido = _ultimo_pedido(messages)
    ultimo = messages[-1] if messages else None
    partes = ultimo.parts if isinstance(ultimo, ModelRequest) else []
    turno_nuevo = any(isinstance(p, UserPromptPart) for p in partes)
    disponibles = {t.name for t in info.function_tools}
    retornos = [
        p
        for p in partes
        if isinstance(p, ToolReturnPart) and p.tool_name in disponibles and not turno_nuevo
    ]
    reintentos = [
        p for p in partes if isinstance(p, RetryPromptPart) and p.tool_name in disponibles
    ]
    if reintentos:
        # Una tool falló: el simulador no reintenta, informa el error y termina.
        texto = (
            f"[simulado] La herramienta {reintentos[0].tool_name} falló: "
            f"{reintentos[0].model_response()[:200]}"
        )
    elif retornos:
        detalle = "; ".join(
            f"{r.tool_name} → {json.dumps(r.content, ensure_ascii=False, default=str)[:260]}"
            for r in retornos
        )
        texto = f"[simulado] Resultado de herramientas: {detalle}"
    else:
        for patron, herramienta, argumentos in REGLAS:
            if herramienta in disponibles and re.search(patron, pedido, re.IGNORECASE):
                return ModelResponse(parts=[ToolCallPart(herramienta, argumentos(pedido))])
        texto = f"[simulado] Respuesta de prueba sin LLM a: «{pedido[:120]}»."
    if info.output_tools:
        herramienta = info.output_tools[0]
        schema = herramienta.parameters_json_schema
        args = _rellenar(schema, schema.get("$defs", {}), texto, pedido)
        return ModelResponse(parts=[ToolCallPart(herramienta.name, args)])
    return ModelResponse(parts=[TextPart(texto)])


def modelo_simulado() -> FunctionModel:
    return FunctionModel(responder, model_name="simulado")
