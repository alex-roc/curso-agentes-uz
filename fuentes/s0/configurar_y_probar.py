# Fuente de notebook Jupyter; regenerar con fuentes/generar_notebooks.py.
# %% [markdown]
# # 0 · Configurar y probar tu entorno
# **Autoría: Alex Ojeda Copa y Lab TecnoSocial**
# **Pregunta:** ¿está todo listo para trabajar: Python, paquetes, ruta de modelo y una respuesta real?
# **Producto:** un diagnóstico de tu entorno y una petición de prueba al modelo.
# **Formato:** opcional y de unos 5 min. Si prefieres la terminal, `bash instalar.sh` (o `instalar.ps1` en PowerShell) hace lo mismo con preguntas guiadas.
# %% [markdown]
# ## 1 · Python y paquetes
# Debe salir Python 3.12 o superior, y ningún paquete en «falta». Si algo falta, cierra Jupyter y ejecuta `uv sync` en la raíz del repositorio; abre Jupyter con `uv run jupyter lab`.
# %%
import sys
from importlib.metadata import PackageNotFoundError, version

print("Python", sys.version.split()[0], "(correcto)" if sys.version_info >= (3, 12) else "(falta 3.12+: usa `uv run`)")
for paquete in ["pydantic-ai-slim", "pydantic-settings", "httpx", "jupyterlab", "rich"]:
    try:
        print(f"  {paquete} {version(paquete)}")
    except PackageNotFoundError:
        print(f"  {paquete}: FALTA (ejecuta `uv sync`)")
# %% [markdown]
# ## 2 · Qué ruta de modelo está activa
# Lee `.env` (nunca muestra las claves). Si no existe `.env`, ejecuta `uv run copiloto-configurar` en una terminal. Recuerda: **`.env` gana sobre las variables de tu terminal**, y los notebooks usan el modelo simulado mientras `COURSE_OFFLINE=1`.
# %%
from copiloto.config import ROOT, Settings, describir_modelo

print(".env existe:", (ROOT / ".env").exists())
s = Settings()
print("MODE =", s.mode, "· COURSE_OFFLINE =", int(s.course_offline))
print("Modelo de la ruta:", describir_modelo(s))
print("Clave de Gemini:", "sí" if s.gemini_api_key.get_secret_value() else "no")
print("Clave de OpenRouter:", "sí" if s.openrouter_api_key.get_secret_value() else "no")
if s.course_offline:
    print("Los notebooks usarán el modelo SIMULADO. Para IA real: COURSE_OFFLINE=0 en .env y reinicia el kernel.")
# %% [markdown]
# ## 3 · Petición de prueba
# Llama de verdad al modelo de tu ruta (ignora `COURSE_OFFLINE`). Con MODE=offline no hay IA que llamar.
# %%
from copiloto.doctor import prueba_en_vivo

if s.mode == "offline":
    print("MODE=offline: no hay modelo real. Configura una ruta con `uv run copiloto-configurar`.")
else:
    try:
        print(prueba_en_vivo(s))
    except Exception as exc:
        print(f"{type(exc).__name__}: {str(exc)[:200]}")
        print("429 = cuota agotada (espera o cambia de modelo); 401/403/400 = clave mal copiada; ConnectError = sin internet u Ollama apagado.")
# %% [markdown]
# ## 4 · Cómo cambiar de ruta
# - **Guiado:** `uv run copiloto-configurar` en la terminal (conserva lo demás de `.env`).
# - **A mano:** edita `.env`: `MODE` (`gemini`, `openrouter`, `local`, `offline`), la clave y el modelo; luego reinicia el kernel.
# - **Comprobar:** `uv run copiloto-doctor --live`.
# - Con las rutas gratuitas tus mensajes pueden usarse para mejorar los productos del proveedor: usa solo datos ficticios.
