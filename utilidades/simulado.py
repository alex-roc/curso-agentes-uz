"""Modelo simulado para practicar sin LLM: elige una tool por palabras clave y resume.

NO es inteligencia artificial. Sirve para ver el ciclo completo (pedido → tool → resultado
→ respuesta tipada) cuando no hay modelo, red o cuota. Funciona con cualquier agente: elige
la tool por el parecido entre su nombre y el pedido, rellena sus argumentos y el `output_type`
con valores mínimos. Su texto empieza con «[simulado]».
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


def _numeros(texto: str) -> list[float]:
    return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", texto)]


_SINONIMOS = {"paraguas": "lluvia", "llover": "lluvia", "llueve": "lluvia", "temperatura": "clima"}
# Verbos de escritura: si el pedido los usa, se prefieren las tools que piden aprobación.
_ESCRIBIR = re.compile(
    r"\b(crea|crear|agendame|agendar|anota|anotar|registra|registrar|programa|añade|anade"
    r"|guarda|guardar|envia|enviar)\b"
)


def _palabras(texto: str) -> set[str]:
    sin_tildes = texto.lower().translate(str.maketrans("áéíóú", "aeiou"))
    crudas = re.findall(r"[a-zñ]+", sin_tildes)
    return {_SINONIMOS.get(p, p)[:5] for p in crudas if len(p) >= 4}


def _elegir_tool(pedido: str, disponibles: dict) -> str | None:
    """La tool cuyo nombre y descripción comparten más palabras con el pedido.

    Compara prefijos de 5 letras sin tildes (con unos pocos sinónimos: «paraguas» → lluvia);
    el nombre pesa el doble que la descripción, y si el pedido usa un verbo de escritura
    («crea», «agenda», «anota»…) gana la tool que pide aprobación. Sin coincidencia
    no se llama a ninguna tool. Es una heurística de juguete: un modelo real decide por
    significado.
    """
    del_pedido = _palabras(pedido)
    escribe = bool(_ESCRIBIR.search(pedido.lower().translate(str.maketrans("áéíóú", "aeiou"))))
    puntos = {
        nombre: 2 * len(_palabras(nombre.replace("_", " ")) & del_pedido)
        + len(_palabras(tool.description or "") & del_pedido)
        + (3 if escribe and tool.kind == "unapproved" else 0)
        for nombre, tool in disponibles.items()
    }
    mejor = max(puntos, key=puntos.get, default=None)
    return mejor if mejor and puntos[mejor] > 0 else None


def _texto_para(campo: str, pedido: str, horas: list[str]) -> str:
    """Un valor de texto plausible según el nombre del argumento (fecha, hora, título…)."""
    nombre = campo.lower()
    if "fecha" in nombre or nombre in {"dia", "día"}:
        fecha = re.search(r"\d{4}-\d{2}-\d{2}", pedido)
        return fecha.group(0) if fecha else ""
    if any(clave in nombre for clave in ("hora", "inicio", "fin")):
        return horas.pop(0) if horas else ""
    if "titulo" in nombre or "título" in nombre or "asunto" in nombre:
        citado = re.search(r"[«\"]([^»\"]+)[»\"]", pedido)
        return citado.group(1) if citado else pedido[:60]
    if "ciudad" in nombre or "lugar" in nombre:
        lugar = re.search(r"\ben ([A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)", pedido)
        return lugar.group(1) if lugar else ""
    return pedido[:120]


def _ultimo_pedido(messages: list[ModelMessage]) -> str:
    for mensaje in reversed(messages):
        if isinstance(mensaje, ModelRequest):
            for parte in mensaje.parts:
                if isinstance(parte, UserPromptPart) and isinstance(parte.content, str):
                    return parte.content
    return ""


def _rellenar(schema: dict, defs: dict, texto: str, pedido: str, numeros: list[float]):
    """Construye un valor mínimo válido para un esquema JSON (salida del agente o args de tool).

    Rellena solo los campos obligatorios; los números salen, en orden, de los que haya en el
    pedido (`numeros`) o valen 0; los textos reciben `texto`.
    """
    if "$ref" in schema:
        return _rellenar(defs[schema["$ref"].split("/")[-1]], defs, texto, pedido, numeros)
    if "enum" in schema:
        return next((v for v in schema["enum"] if str(v) in pedido.lower()), schema["enum"][0])
    if "anyOf" in schema:
        return _rellenar(schema["anyOf"][0], defs, texto, pedido, numeros)
    tipo = schema.get("type")
    if tipo == "object":
        props = schema.get("properties", {})
        horas = re.findall(r"\b\d{1,2}:\d{2}\b", pedido)
        valores = {}
        for k, v in props.items():
            if k not in schema.get("required", []):
                continue
            if v.get("type") == "string" and "enum" not in v and texto is pedido:
                valores[k] = _texto_para(k, pedido, horas)  # argumentos de una tool
            else:
                valores[k] = _rellenar(v, defs, texto, pedido, numeros)
        return valores
    if tipo == "array":
        item = schema.get("items", {})
        return [] if item.get("type") != "string" else [texto[:120]]
    if tipo == "boolean":
        return False
    if tipo in {"integer", "number"}:
        valor = numeros.pop(0) if numeros else 0
        return int(valor) if tipo == "integer" else valor
    return texto


def responder(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    pedido = _ultimo_pedido(messages)
    ultimo = messages[-1] if messages else None
    partes = ultimo.parts if isinstance(ultimo, ModelRequest) else []
    turno_nuevo = any(isinstance(p, UserPromptPart) for p in partes)
    disponibles = {t.name: t for t in info.function_tools}
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
        herramienta = _elegir_tool(pedido, disponibles)
        if herramienta:
            schema = disponibles[herramienta].parameters_json_schema
            args = _rellenar(schema, schema.get("$defs", {}), pedido, pedido, _numeros(pedido))
            return ModelResponse(parts=[ToolCallPart(herramienta, args)])
        texto = f"[simulado] Respuesta de prueba sin LLM a: «{pedido[:120]}»."
    if info.output_tools:
        herramienta = info.output_tools[0]
        schema = herramienta.parameters_json_schema
        args = _rellenar(schema, schema.get("$defs", {}), texto, pedido, [])
        return ModelResponse(parts=[ToolCallPart(herramienta.name, args)])
    return ModelResponse(parts=[TextPart(texto)])


def modelo_simulado() -> FunctionModel:
    """El modelo que recibe `Agent(...)` cuando la ruta es el modo simulado."""
    return FunctionModel(responder, model_name="simulado")
