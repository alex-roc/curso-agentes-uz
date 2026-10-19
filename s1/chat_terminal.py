"""Terminal de chat con Mi copiloto: un agente de Pydantic AI con dos tools, en la terminal.

    uv run python s1/chat_terminal.py             # usa la ruta de MODE en tu .env
    uv run python s1/chat_terminal.py --offline   # modelo simulado, sin LLM ni red

Muestra la respuesta en Markdown (con streaming si el modelo lo permite), cada tool que
el agente decide usar, el uso por turno y comandos para inspeccionar el recorrido.
Escribe /ayuda. La alternativa de una línea de Pydantic AI es `agente.to_cli_sync()`.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

import httpx
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.usage import RunUsage
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner

from copiloto.config import Settings, crear_modelo, describir_modelo
from copiloto.herramientas import calcular_presupuesto

INSTRUCCIONES = """Eres Mi copiloto, el asistente personal de Alex. Responde en español, breve.
Usa las herramientas para calcular presupuestos y para saber la fecha y la hora; no las inventes.
Si no tienes un dato, dilo."""

AYUDA = """**Comandos**
- `/ayuda` esta lista · `/modelo` la ruta activa · `/uso` consumo de la sesión
- `/mensajes` recorrido del último turno (pedido, tools, respuesta)
- `/borrar` olvida la conversación · `/salir` termina (también Ctrl+C o Ctrl+D)

**Prueba:** «¿Qué hora es?» o «Calcula el presupuesto de 3 horas a 40 Bs por hora»."""

console = Console()


def hora_actual() -> dict:
    """Fecha y hora actuales en La Paz, Bolivia (UTC-4, sin horario de verano)."""
    ahora = datetime.now(timezone(timedelta(hours=-4)))
    return {
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M"),
        "zona": "America/La_Paz",
    }


def tenue(texto: str, n: int = 140) -> None:
    console.print(f"  [dim]{texto if len(texto) <= n else texto[: n - 1] + '…'}[/dim]")


def mostrar_recorrido(mensajes: list[ModelMessage]) -> None:
    """Pedido → tools → resultados → respuesta, leído de los mensajes tipados."""
    for m in mensajes:
        for p in m.parts:
            if isinstance(m, ModelRequest) and isinstance(p, UserPromptPart):
                tenue(f"persona   {p.content}")
            elif isinstance(p, ToolCallPart):
                tenue(f"pide tool {p.tool_name}({p.args_as_dict()})")
            elif isinstance(p, ToolReturnPart):
                tenue(f"resultado {p.tool_name} → {p.content}")
            elif isinstance(m, ModelResponse) and isinstance(p, TextPart):
                tenue(f"respuesta {p.content}")


def explicar(exc: Exception) -> str:
    """Un mensaje amable por tipo de fallo, sin traceback."""
    estado = exc.status_code if isinstance(exc, ModelHTTPError) else None
    if estado == 429:
        return "Cuota o ritmo agotado (429): espera un minuto o cambia de modelo en .env."
    if estado in (401, 403) or (estado == 400 and "API key" in str(exc)):  # Gemini da 400
        return "El proveedor rechazó la clave (401/403): revisa la clave en .env."
    if estado == 404:
        return "Modelo no encontrado (404): revisa el nombre del modelo en .env."
    causa = exc.__cause__ or exc
    if (
        isinstance(causa, (httpx.ConnectError, ConnectionError))
        or "Connection" in type(causa).__name__
    ):
        return "No hay conexión con el modelo. Si usas Ollama, ¿está activo? (docs/ollama.md)"
    return f"{type(exc).__name__}: {str(exc)[:200]}"


async def turno(agente: Agent, pedido: str, historial, settings: Settings, streaming: bool):
    """Ejecuta un turno. Con streaming, la respuesta se dibuja a medida que llega."""
    limites = UsageLimits(request_limit=settings.request_limit)
    if not streaming:
        with console.status("pensando…"):
            r = await agente.run(pedido, message_history=historial, usage_limits=limites)
        mostrar_recorrido(
            [
                m
                for m in r.new_messages()
                if any(isinstance(p, (ToolCallPart, ToolReturnPart)) for p in m.parts)
            ]
        )
        console.print(Markdown(r.output))
        return r

    texto = ""
    with Live(Spinner("dots", text="pensando…"), console=console, transient=True) as vivo:

        async def eventos(ctx, flujo) -> None:
            nonlocal texto
            async for e in flujo:
                if isinstance(e, PartStartEvent) and isinstance(e.part, TextPart):
                    texto += e.part.content
                elif isinstance(e, PartDeltaEvent) and isinstance(e.delta, TextPartDelta):
                    texto += e.delta.content_delta
                elif isinstance(e, FunctionToolCallEvent):
                    vivo.console.print(
                        f"  [dim]pide tool {e.part.tool_name}({e.part.args_as_dict()})[/dim]"
                    )
                elif isinstance(e, FunctionToolResultEvent):
                    p = e.part  # ToolReturnPart, o RetryPromptPart si la tool falló
                    resultado = p.content if isinstance(p, ToolReturnPart) else p.model_response()
                    vivo.console.print(f"  [dim]resultado {str(resultado)[:140]}[/dim]")
                    texto = ""  # el texto previo a una tool no es la respuesta final
                if texto:
                    vivo.update(Markdown(texto))

        r = await agente.run(
            pedido, message_history=historial, usage_limits=limites, event_stream_handler=eventos
        )
    console.print(Markdown(r.output))  # el borrador en vivo desaparece y queda la versión final
    return r


async def chat() -> None:
    settings = Settings()
    offline = "--offline" in sys.argv
    try:
        agente = Agent(
            crear_modelo(settings, offline),
            instructions=INSTRUCCIONES,
            tools=[calcular_presupuesto, hora_actual],
            name="mi-copiloto-terminal",
        )
    except ValueError as exc:  # falta una clave o un modelo
        sys.exit(f"Error: {exc}")
    activo = describir_modelo(settings, offline)
    console.rule(f"[bold]Mi copiloto[/bold] · {activo}")
    console.print("[dim]Escribe /ayuda para ver los comandos.[/dim]")
    historial: list[ModelMessage] = []  # la memoria de corto plazo: todos los mensajes
    ultimo_turno: list[ModelMessage] = []
    total = RunUsage()
    while True:
        try:
            pedido = console.input("\n[bold cyan]Tú >[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pedido == "/salir":
            break
        if pedido == "/ayuda":
            console.print(Markdown(AYUDA))
        elif pedido == "/borrar":
            historial, ultimo_turno = [], []
            console.print("[dim](conversación borrada)[/dim]")
        elif pedido == "/modelo":
            console.print(
                f"Modelo: [bold]{activo}[/bold] · MODE={'offline' if offline else settings.mode}"
            )
        elif pedido == "/uso":
            console.print(
                f"Sesión: {total.requests} requests · {total.input_tokens} tokens de entrada · {total.output_tokens} de salida"
            )
        elif pedido == "/mensajes":
            mostrar_recorrido(ultimo_turno) if ultimo_turno else console.print(
                "[dim](aún no hay turnos)[/dim]"
            )
        elif pedido.startswith("/"):
            console.print("Comando desconocido. Prueba /ayuda.")
        elif pedido:
            try:
                r = await turno(agente, pedido, historial, settings, streaming=not offline)
            except KeyboardInterrupt:
                break
            except Exception as exc:  # red, clave, cuota o modelo: falla el programa, no el chat
                console.print(f"[red]No pude responder.[/red] {explicar(exc)}")
                continue
            historial, ultimo_turno = r.all_messages(), r.new_messages()
            total.incr(r.usage)
            u = r.usage
            console.print(
                f"  [dim]{u.requests} requests · {u.input_tokens} tokens de entrada · {u.output_tokens} de salida[/dim]"
            )
    console.print("\nHasta luego.")


if __name__ == "__main__":
    asyncio.run(chat())
