"""La terminal de Mi copiloto (nace en la sesión 1).

    uv run python -m mi_copiloto.chat              # con la ruta de tu .env (COURSE_OFFLINE=0)
    uv run python -m mi_copiloto.chat --modo gemini   # otra ruta: local, gemini u openrouter
    uv run python -m mi_copiloto.chat --simulado   # sin IA: el modelo simulado

Dentro: /borrar empieza de cero y /salir termina. Cada turno muestra las tools que se ejecutan
(líneas grises) y, si el agente pide una acción que escribe, pregunta [s/N] antes de ejecutarla.
"""

import argparse
import asyncio
import sys

from pydantic_ai import DeferredToolRequests, DeferredToolResults, ToolDenied, UsageLimits
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from rich.console import Console
from rich.markdown import Markdown

from utilidades.config import crear_modelo, describir_ruta
from utilidades.practica import preparar

from .agente import Deps, crear_agente

consola = Console()


def mostrar_trazas(mensajes) -> None:
    """Imprime en gris cada tool que pidió el modelo y lo que devolvió."""
    for mensaje in mensajes:
        for parte in mensaje.parts:
            if isinstance(parte, ToolCallPart):
                consola.print(f"[dim]🤖 {parte.tool_name}({parte.args_as_dict()})[/dim]")
            elif isinstance(parte, ToolReturnPart):
                consola.print(f"[dim]🔧 {str(parte.content)[:140]}[/dim]")


def decidir(solicitudes: DeferredToolRequests) -> DeferredToolResults:
    """La persona decide, fuera del modelo: True aprueba y ToolDenied rechaza."""
    decisiones = {}
    for llamada in solicitudes.approvals:
        consola.print(
            f"[yellow]¿Apruebas {llamada.tool_name}({llamada.args_as_dict()})? [s/N][/yellow]"
        )
        respuesta = input("› ").strip().lower()
        decisiones[llamada.tool_call_id] = (
            True if respuesta in {"s", "si", "sí"} else ToolDenied("No")
        )
    return DeferredToolResults(approvals=decisiones)


async def turno(agente, deps: Deps, texto: str, historial: list) -> list:
    """Un turno: ejecuta el agente y, mientras pida aprobación, pregunta y reanuda."""
    limites = UsageLimits(request_limit=10)  # el control más barato contra un bucle sin fin
    resultado = await agente.run(texto, message_history=historial, deps=deps, usage_limits=limites)
    mostrar_trazas(resultado.new_messages())
    while isinstance(resultado.output, DeferredToolRequests):
        resultado = await agente.run(
            None,  # no hay mensaje nuevo: solo la decisión de la persona
            message_history=resultado.all_messages(),
            deferred_tool_results=decidir(resultado.output),
            deps=deps,
            usage_limits=limites,
        )
        mostrar_trazas(resultado.new_messages())
    respuesta = resultado.output
    consola.print(Markdown(respuesta.texto))
    if respuesta.fuentes:
        consola.print(f"[dim]fuentes: {', '.join(respuesta.fuentes)}[/dim]")
    return resultado.all_messages()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Terminal de Mi copiloto")
    parser.add_argument("--simulado", action="store_true", help="modelo simulado, sin IA real")
    parser.add_argument("--modo", choices=["local", "gemini", "openrouter"], help="ruta de modelo")
    args = parser.parse_args()
    settings, offline = preparar(**({"mode": args.modo} if args.modo else {}))
    offline = offline or args.simulado
    agente = crear_agente(crear_modelo(settings, offline))
    deps = Deps(sin_red=offline)
    historial: list = []
    consola.print(
        f"[bold]Mi copiloto[/bold] · {describir_ruta(settings, offline)} · /borrar · /salir"
    )
    while True:
        try:
            texto = input("tú › ").strip()
        except EOFError:  # entrada por tubería: se acabaron las líneas
            break
        if texto == "/salir":
            break
        if texto == "/borrar":
            historial, deps.eventos_nuevos = [], []
            consola.print("[dim]Historial borrado.[/dim]")
        elif texto:
            try:
                historial = await turno(agente, deps, texto, historial)
            except Exception as exc:  # falla el modelo o la red: se explica y se sigue
                consola.print(f"[red]Falló el turno ({type(exc).__name__}): {str(exc)[:200]}[/red]")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows
    asyncio.run(main())
