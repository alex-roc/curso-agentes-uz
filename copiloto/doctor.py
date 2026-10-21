"""Diagnóstico: `uv run copiloto-doctor` (config) y `uv run copiloto-doctor --live` (llama al modelo)."""

import asyncio
import sys

from .agente import crear_agente_basico
from .config import Settings, describir_modelo, validar_ruta


async def prueba_en_vivo(settings: Settings) -> str:
    """Una llamada real al modelo de la ruta activa; lanza la excepción del proveedor si falla.

    Es async para que funcione en un notebook (`await prueba_en_vivo(s)`), donde ya hay un
    bucle de eventos; desde un script se llama con `asyncio.run(...)`.
    """
    resultado = await crear_agente_basico(settings).run("Salúdame en una frase.")
    return resultado.output.texto


def main() -> None:
    settings = Settings()
    print(f"Ruta: MODE={settings.mode} · modelo={describir_modelo(settings)}")
    if settings.mode == "offline":
        print("✅ Modo simulado: no hace falta nada más.")
        return
    try:
        validar_ruta(settings)
    except ValueError as exc:
        sys.exit(f"❌ {exc}")
    print("✅ La configuración de la ruta está completa.")
    if "--live" not in sys.argv:
        print("Añade --live para probar una llamada real al modelo.")
        return
    try:
        print("✅ El modelo respondió:", asyncio.run(prueba_en_vivo(settings)))
    except Exception as exc:  # red, clave, cuota o modelo no descargado: falla el programa
        sys.exit(f"❌ {type(exc).__name__}: {str(exc)[:200]}")


if __name__ == "__main__":
    main()
