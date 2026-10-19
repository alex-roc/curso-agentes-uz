"""Diagnóstico: `uv run copiloto-doctor` (config) y `uv run copiloto-doctor --live` (llama al modelo)."""

import sys

from .agente import crear_agente_basico
from .config import Settings, describir_modelo, validar_ruta


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
        r = crear_agente_basico(settings).run_sync("Salúdame en una frase.")
    except Exception as exc:  # red, clave, cuota o modelo no descargado: falla el programa
        sys.exit(f"❌ {type(exc).__name__}: {str(exc)[:200]}")
    print("✅ El modelo respondió:", r.output.texto)


if __name__ == "__main__":
    main()
