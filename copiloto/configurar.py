"""Configurador del curso: `uv run copiloto-configurar` deja `.env` listo y prueba el modelo.

Interactivo por defecto. Para automatizar (o probar): `--ruta gemini|openrouter|local|simulado`,
`--modelo ID`, la clave en la variable `COPILOTO_CLAVE` y `--sin-prueba`.
"""

import argparse
import getpass
import os
import shutil
import subprocess
import sys
import warnings

import httpx
from rich.console import Console

from .config import ROOT, Settings, describir_modelo
from .doctor import prueba_en_vivo

consola = Console(highlight=False)
ENV = ROOT / ".env"
EJEMPLO = ROOT / ".env.example"
OPENROUTER_MODELOS = "https://openrouter.ai/api/v1/models"
RUTAS = {
    "gemini": ("MODE=gemini", "GEMINI_API_KEY", ("AIza", "AQ."), "https://aistudio.google.com/apikey"),
    "openrouter": ("MODE=openrouter", "OPENROUTER_API_KEY", ("sk-or-",), "https://openrouter.ai/keys"),
}
PRIVACIDAD = (
    "[yellow]Privacidad:[/] con las capas gratuitas de Gemini y OpenRouter lo que escribes viaja "
    "al proveedor y puede usarse para mejorar sus productos. Usa solo datos ficticios."
)


# ── .env ────────────────────────────────────────────────────────────────
def leer_env() -> dict[str, str]:
    valores: dict[str, str] = {}
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                valores[k.strip()] = v.strip().strip("\"'")
    return valores


def escribir_env(cambios: dict[str, str]) -> None:
    """Actualiza solo las claves indicadas; conserva comentarios y el resto de valores."""
    if not ENV.exists():
        ENV.write_text(EJEMPLO.read_text(encoding="utf-8"), encoding="utf-8")
    lineas = ENV.read_text(encoding="utf-8").splitlines()
    pendientes = dict(cambios)
    for i, linea in enumerate(lineas):
        clave = linea.split("=", 1)[0].strip()
        if "=" in linea and not linea.lstrip().startswith("#") and clave in pendientes:
            lineas[i] = f"{clave}={pendientes.pop(clave)}"
    lineas += [f"{k}={v}" for k, v in pendientes.items()]
    ENV.write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ── Entrada ─────────────────────────────────────────────────────────────
def preguntar(texto: str, defecto: str = "") -> str:
    try:
        r = input(f"{texto}{f' [{defecto}]' if defecto else ''}: ").strip()
    except EOFError:
        r = ""
    return r or defecto


def confirmar(texto: str, defecto: bool = True) -> bool:
    r = preguntar(f"{texto} ({'S/n' if defecto else 's/N'})").lower()
    return defecto if not r else r[0] in "sy"


def revisar_clave(clave: str, prefijos: tuple[str, ...]) -> bool:
    """Rechaza lo que claramente no es una clave; un prefijo raro solo avisa (los formatos cambian)."""
    if len(clave) < 20 or any(c in clave for c in " \"'"):
        consola.print("[red]Eso no parece una clave: revisa que la copiaste completa, sin comillas ni espacios.[/]")
        return False
    if not clave.startswith(prefijos):
        consola.print(
            f"[yellow]Aviso: las claves suelen empezar con «{'» o «'.join(prefijos)}». La prueba en vivo dirá si funciona.[/]"
        )
    return True


def pedir_clave(nombre: str, prefijo: tuple[str, ...], url: str) -> str:
    consola.print(f"Crea una clave gratis en [cyan]{url}[/] y pégala aquí. No se verá al escribir.")
    for _ in range(3):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # getpass avisa si la entrada es una tubería
            clave = getpass.getpass(f"{nombre}: ").strip()
        if revisar_clave(clave, prefijo):
            return clave
    sys.exit("No se recibió una clave válida. Vuelve a ejecutar `uv run copiloto-configurar`.")


# ── Rutas ───────────────────────────────────────────────────────────────
def modelos_openrouter_gratis() -> list[str]:
    datos = httpx.get(OPENROUTER_MODELOS, timeout=20).raise_for_status().json()["data"]
    ids = [
        m["id"]
        for m in datos
        if m["id"].endswith(":free") and "tools" in (m.get("supported_parameters") or [])
    ]
    return sorted(ids)


def elegir_modelo_openrouter(modelo: str | None, interactivo: bool) -> str:
    if modelo:
        return modelo
    try:
        ids = modelos_openrouter_gratis()
    except Exception as exc:
        consola.print(f"[yellow]No pude leer el catálogo de OpenRouter ({type(exc).__name__}).[/]")
        ids = []
    if not ids:
        return preguntar("Escribe el ID de un modelo que termine en :free (docs/openrouter.md)")
    if not interactivo:
        return ids[0]
    consola.print("Modelos gratuitos con tools (el catálogo cambia cada semana):")
    for n, i in enumerate(ids[:20], 1):
        consola.print(f"  {n:>2}. {i}")
    r = preguntar("Número o ID del modelo", "1")
    return ids[int(r) - 1] if r.isdigit() and 0 < int(r) <= min(20, len(ids)) else r


def ollama_responde(url: str) -> list[str] | None:
    try:
        r = httpx.get(url.rstrip("/") + "/api/tags", timeout=3).raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return None


def preparar_ollama(modelo: str, url: str, interactivo: bool) -> bool:
    """True si Ollama responde y el modelo está descargado (ofrece descargarlo)."""
    if not shutil.which("ollama"):
        consola.print("[red]No encuentro Ollama.[/] Instálalo desde https://ollama.com/download")
        return False
    modelos = ollama_responde(url)
    if modelos is None:
        consola.print("[red]Ollama está instalado pero no responde en " + url + ".[/]")
        consola.print("Ábrelo (app de Ollama) o ejecuta `ollama serve` en otra terminal.")
        return False
    if any(m == modelo or m.split(":")[0] == modelo for m in modelos):
        return True
    consola.print(f"Falta el modelo [bold]{modelo}[/] (unos 2,5 GB de descarga).")
    if interactivo and not confirmar("¿Descargarlo ahora con `ollama pull`?"):
        return False
    return subprocess.run(["ollama", "pull", modelo]).returncode == 0


AYUDA_ERRORES = (
    ("429", "Cuota gratuita agotada. Espera un minuto, cambia `GEMINI_MODEL` en `.env` o usa otra ruta."),
    ("401", "Clave rechazada. Vuelve a ejecutar `uv run copiloto-configurar` y pégala de nuevo."),
    ("403", "Clave sin permiso (o proyecto con facturación). Crea una nueva en un proyecto gratuito."),
    ("400", "Petición rechazada: casi siempre una clave mal copiada. Créala de nuevo."),
    ("Connect", "No hay conexión con el modelo: sin internet o Ollama apagado (`ollama serve`)."),
    ("not found", "Ese modelo no existe en tu cuenta o en tu Ollama: revisa el nombre en `.env`."),
)


def probar(settings: Settings) -> bool:
    consola.print(f"Probando el modelo [bold]{describir_modelo(settings)}[/] (puede tardar)…")
    try:
        texto = prueba_en_vivo(settings)
    except Exception as exc:
        detalle = f"{type(exc).__name__}: {exc}"
        consola.print(f"[red]✗ Falló la prueba:[/] {detalle[:200]}")
        for patron, ayuda in AYUDA_ERRORES:
            if patron.lower() in detalle.lower():
                consola.print(f"  → {ayuda}")
                break
        return False
    consola.print(f"[green]✓ El modelo respondió:[/] {texto}")
    return True


def avisar_entorno(clave_env: str, escrita: str) -> None:
    """Si la terminal exporta otra clave, el curso usa igualmente la de `.env` (ver config.py)."""
    otra = os.environ.get(clave_env, "")
    if otra and otra != escrita:
        consola.print(
            f"[yellow]Tu terminal exporta una {clave_env} distinta.[/] El curso usa la de `.env`, "
            "pero otros programas usarían la exportada. Para quitarla en esta terminal: "
            f"`unset {clave_env}` (macOS, Linux, Git Bash) o `Remove-Item Env:{clave_env}` (PowerShell)."
        )


# ── Programa ────────────────────────────────────────────────────────────
def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Configura .env y prueba tu ruta de modelo.")
    ap.add_argument("--ruta", choices=["gemini", "openrouter", "local", "simulado"])
    ap.add_argument("--modelo", help="ID del modelo (por defecto, el de .env o el recomendado)")
    ap.add_argument("--sin-prueba", action="store_true", help="no llamar al modelo al terminar")
    args = ap.parse_args()
    interactivo = args.ruta is None
    actual = leer_env()

    consola.print("[bold]Configuración del curso «Más allá de los chatbots»[/]\n")
    ruta = args.ruta
    if interactivo:
        consola.print(
            "¿Con qué modelo quieres trabajar?\n"
            "  1. [bold]Gemini gratis[/]: la más fácil para empezar. Clave gratuita de Google, sin tarjeta.\n"
            "  2. [bold]OpenRouter :free[/]: modelos abiertos en la nube, 50 peticiones por día.\n"
            "  3. [bold]Ollama local[/]: corre en tu equipo (~2,5 GB), datos privados; pide RAM.\n"
            "  4. [bold]Simulado[/]: sin IA; solo muestra el recorrido de un agente.\n"
        )
        ruta = {"1": "gemini", "2": "openrouter", "3": "local", "4": "simulado"}.get(
            preguntar("Elige 1, 2, 3 o 4", "1")
        )
        if not ruta:
            sys.exit("Opción no válida.")

    cambios: dict[str, str] = {}
    if ruta == "simulado":
        cambios = {"MODE": "offline", "COURSE_OFFLINE": "1"}
    elif ruta == "local":
        modelo = args.modelo or actual.get("OLLAMA_MODEL") or "qwen3:4b-instruct"
        url = actual.get("OLLAMA_BASE_URL") or "http://localhost:11434"
        if not preparar_ollama(modelo, url, interactivo):
            sys.exit("Deja Ollama listo (docs/ollama.md) y vuelve a ejecutar el configurador.")
        cambios = {"MODE": "local", "COURSE_OFFLINE": "0", "OLLAMA_MODEL": modelo}
    else:
        _, nombre_clave, prefijo, url = RUTAS[ruta]
        clave = os.environ.get("COPILOTO_CLAVE", "").strip()
        if not clave and actual.get(nombre_clave):
            if interactivo and not confirmar(f"Ya hay una {nombre_clave} en .env. ¿Conservarla?"):
                clave = pedir_clave(nombre_clave, prefijo, url)
            else:
                clave = actual[nombre_clave]
        elif not clave:
            if not interactivo:
                sys.exit(f"Falta la clave: define COPILOTO_CLAVE o {nombre_clave} en .env.")
            clave = pedir_clave(nombre_clave, prefijo, url)
        if not revisar_clave(clave, prefijo):
            sys.exit("La clave no parece válida. Vuelve a ejecutar `uv run copiloto-configurar`.")
        cambios = {"MODE": ruta, "COURSE_OFFLINE": "0", nombre_clave: clave}
        if ruta == "openrouter":
            cambios["OPENROUTER_MODEL"] = elegir_modelo_openrouter(
                args.modelo or (None if interactivo else actual.get("OPENROUTER_MODEL")),
                interactivo,
            )
        elif args.modelo:
            cambios["GEMINI_MODEL"] = args.modelo
        avisar_entorno(nombre_clave, clave)

    escribir_env(cambios)
    consola.print(f"[green]✓ Guardé tu configuración en {ENV.name}[/] (nunca se sube a Git).")
    if ruta in RUTAS:
        consola.print(PRIVACIDAD)
    ok = True
    if ruta != "simulado" and not args.sin_prueba:
        ok = probar(Settings())
    consola.print()
    if ok:
        consola.print(
            "[bold green]Listo.[/] Abre Jupyter con [bold]uv run jupyter lab[/] y empieza por "
            "[bold]s1/01_primer_agente.ipynb[/].\nO conversa en la terminal: "
            "[bold]uv run python s1/chat_terminal.py[/]. Para cambiar de ruta, repite "
            "`uv run copiloto-configurar`."
        )
    else:
        consola.print(
            "[yellow]La configuración quedó guardada, pero la prueba falló.[/] Corrige lo indicado y "
            "repite `uv run copiloto-configurar` (o `uv run copiloto-doctor --live`)."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
