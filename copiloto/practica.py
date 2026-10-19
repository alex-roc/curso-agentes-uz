"""Utilidades para los notebooks: preparar el entorno, ver qué pasó y autocorregir ejercicios."""

import json
from collections.abc import Callable

from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)

from .config import ROOT, Settings, describir_modelo


def preparar(**cambios) -> tuple[Settings, bool]:
    """Lee .env y decide el modo. Por defecto los notebooks arrancan sin LLM (COURSE_OFFLINE=1)."""
    settings = Settings(_env_file=ROOT / ".env", **cambios)
    offline = settings.offline or settings.course_offline
    if offline:
        settings = settings.model_copy(update={"mode": "offline"})
    print(f"Modelo: {describir_modelo(settings)}")
    if offline:
        print(
            "Modo práctica sin LLM: el modelo simulado NO mide calidad. "
            "Pon COURSE_OFFLINE=0 en .env (y reinicia el kernel) para usar IA real."
        )
    return settings, offline


def _corto(valor, n: int = 160) -> str:
    texto = valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, default=str)
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def ver_mensajes(resultado, n: int = 160) -> None:
    """Muestra el recorrido de una ejecución: pedido → tools → resultados → respuesta."""
    for mensaje in resultado.all_messages():
        for parte in mensaje.parts:
            if isinstance(mensaje, ModelRequest) and isinstance(parte, UserPromptPart):
                print(f"👤 persona   {_corto(parte.content, n)}")
            elif isinstance(parte, ToolCallPart):
                print(f"🤖 pide tool {parte.tool_name}({_corto(parte.args_as_dict(), n)})")
            elif isinstance(parte, ToolReturnPart):
                print(f"🔧 resultado {parte.tool_name} → {_corto(parte.content, n)}")
            elif isinstance(parte, RetryPromptPart):
                print(f"↩️  reintento {_corto(parte.model_response(), n)}")
            elif isinstance(mensaje, ModelResponse) and isinstance(parte, TextPart):
                print(f"🤖 texto     {_corto(parte.content, n)}")
    print(f"   requests={resultado.usage.requests}")


def revisar(nombre: str, condicion: Callable[[], bool] | bool, pista: str = "") -> bool:
    """Autocorrección amable: nunca rompe el notebook, dice qué falta."""
    try:
        ok = condicion() if callable(condicion) else bool(condicion)
    except Exception as exc:  # el ejercicio aún no está completo
        ok, pista = False, f"{pista} ({type(exc).__name__}: {str(exc)[:120]})"
    print(f"✅ {nombre}" if ok else f"⏳ {nombre}: {pista}")
    return ok
