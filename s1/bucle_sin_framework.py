"""El bucle de un agente, sin framework y con una sola interfaz de «modelo».

Un modelo es cualquier función `llamar(mensajes) -> mensaje` en el formato de la API compatible
con OpenAI (Ollama, Gemini y OpenRouter la hablan). El bucle no sabe si detrás hay un modelo
de juguete o un LLM real: por eso cambiar de proveedor no toca el agente.

    uv run python s1/bucle_sin_framework.py              # modelo de juguete y LLM real
    uv run python s1/bucle_sin_framework.py --sin-llm    # solo el de juguete (sin red)
"""

import json
import re
import sys

import httpx

from copiloto.config import Settings, describir_modelo, ruta_openai
from copiloto.herramientas import calcular_presupuesto

PEDIDO = "Calcula el presupuesto de 3 horas de taller a 40 Bs por hora."

# Lista blanca: solo se ejecuta lo que está aquí. El esquema que ve el modelo va aparte y a mano.
TOOLS = {"calcular_presupuesto": calcular_presupuesto}
ESQUEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calcular_presupuesto",
            "description": "Calcula el costo en Bs según horas y tarifa por hora.",
            "parameters": {
                "type": "object",
                "properties": {"horas": {"type": "number"}, "tarifa": {"type": "number"}},
                "required": ["horas", "tarifa"],
            },
        },
    }
]


def agente(pedido: str, llamar, max_pasos: int = 5) -> str:
    """El bucle: el modelo propone, el programa ejecuta, se repite hasta una respuesta o el límite."""
    mensajes = [{"role": "user", "content": pedido}]
    for _ in range(max_pasos):
        mensaje = llamar(mensajes)
        mensajes.append(mensaje)
        if not mensaje.get("tool_calls"):
            return mensaje["content"]
        for pedida in mensaje["tool_calls"]:
            f = pedida["function"]
            resultado = json.dumps(TOOLS[f["name"]](**json.loads(f["arguments"])))
            print(f"🤖 pide {f['name']}({f['arguments']}) → 🔧 {resultado}")
            mensajes.append({"role": "tool", "tool_call_id": pedida["id"], "content": resultado})
    raise RuntimeError(f"Sin respuesta tras {max_pasos} pasos")


def modelo_juguete(mensajes: list[dict]) -> dict:
    """Un «modelo» de mentira con reglas fijas. No es IA."""
    if mensajes[-1]["role"] == "tool":
        total = json.loads(mensajes[-1]["content"])["total"]
        return {"role": "assistant", "content": f"El presupuesto es {total} Bs."}
    horas, tarifa = re.findall(r"\d+", mensajes[-1]["content"])[:2]
    args = json.dumps({"horas": float(horas), "tarifa": float(tarifa)})
    pedida = {"id": "1", "function": {"name": "calcular_presupuesto", "arguments": args}}
    return {"role": "assistant", "content": "", "tool_calls": [pedida]}


def modelo_real(settings: Settings):
    """Un LLM real: el mismo contrato, enviado por HTTP. Solo cambian URL, clave y modelo."""
    base, clave, modelo = ruta_openai(settings)

    def llamar(mensajes: list[dict]) -> dict:
        r = httpx.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {clave}"},
            json={"model": modelo, "messages": mensajes, "tools": ESQUEMAS, "temperature": 0},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]

    return llamar


def main() -> None:
    print("== Modelo de juguete ==")
    print("✅", agente(PEDIDO, modelo_juguete))
    if "--sin-llm" in sys.argv:
        return
    settings = Settings()
    if settings.mode == "offline":
        print("\nMODE=offline: no hay LLM. Cambia MODE en .env para probar uno real.")
        return
    print(f"\n== LLM real: {describir_modelo(settings)} ==")
    try:
        print("✅", agente(PEDIDO, modelo_real(settings)))
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        sys.exit(
            f"❌ {type(exc).__name__}: {str(exc)[:200]}\nPrueba: uv run copiloto-doctor --live"
        )


if __name__ == "__main__":
    main()
