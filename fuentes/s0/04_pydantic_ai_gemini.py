# Fuente de notebook Jupyter con top-level await; regenerar con fuentes/generar_notebooks.py.
# ruff: noqa: F704
# %% [markdown]
# # Tarea S0 · Pydantic AI con tu clave gratuita de Gemini
# **Pregunta:** ¿puedo conectar mi propio código con un modelo real de IA, controlar sus errores y pedirle datos estructurados?
# **Producto:** un agente de Pydantic AI que responde con Gemini, una comparación de dos modelos y un reto opcional (texto libre a un `Gasto`), con autocorrección (✅/⏳).
# **Al terminar:** habrás comprobado tu configuración sin exponer la clave, creado un `Agent` con `GoogleModel`, manejado errores de cuota y de clave, leído el uso de tokens y comparado dos modelos.
# **Formato:** tarea autónoma de unos 30 a 45 min; necesita red y una clave gratuita de Google AI Studio. Va después de `03_ejercicios.ipynb`. Se revisa al inicio de la sesión 1.
# **Cómo se usa:** completa cada celda marcada con `TODO` y ejecuta la celda `comprobar(...)` que sigue. Los ejercicios 2 y 3 se autocorrigen sin red; el 4, el 5 y el reto necesitan IA real.
# %%
from datetime import date

from copiloto.practica import preparar, revisar

settings, OFFLINE = preparar()
HOY = date(2030, 5, 14)
RESULTADOS: dict[str, bool] = {}


def comprobar(nombre: str, condicion, pista: str = "") -> None:
    """Como `revisar`, pero apunta el resultado para el recuento final."""
    RESULTADOS[nombre] = revisar(nombre, condicion, pista)
# %% [markdown]
# # Conexión con Pydantic AI y tu clave gratuita de Gemini
# Ahora hablas con un modelo **real**. Necesitas una clave **gratuita** de Google AI Studio (sin tarjeta; no vincules facturación). Si aún no la tienes: `uv run copiloto-configurar --ruta gemini` te la pide sin mostrarla y la guarda en `.env`; o créala en https://aistudio.google.com/apikey. Para usarla pon además `COURSE_OFFLINE=0` en `.env` (el configurador ya lo hace) y reinicia el kernel. **Nunca** pegues la clave en el notebook ni la subas a GitHub. Usa solo datos ficticios.
# %% [markdown]
# ## Ejercicio 1 · Comprobar la configuración
# Comprueba Comprueba la configuración **sin imprimir la clave** (solo si existe y cuántos caracteres tiene). Ejecuta la celda tal cual.
# %%
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from copiloto.config import ROOT, Settings

ajustes = Settings(_env_file=ROOT / ".env")
clave = ajustes.gemini_api_key.get_secret_value()
print(f"MODE={ajustes.mode} · modelo={ajustes.gemini_model} · simulado={OFFLINE}")
print(f"GEMINI_API_KEY: {'presente, ' + str(len(clave)) + ' caracteres' if clave else 'NO está en .env'}")
if not clave:
    print("→ Ejecuta `uv run copiloto-configurar --ruta gemini` o crea la clave en https://aistudio.google.com/apikey")
if OFFLINE:
    print("→ Estás en modo simulado: pon COURSE_OFFLINE=0 en .env y reinicia el kernel para la parte con red.")
LISTO_PARA_RED = bool(clave) and not OFFLINE
# %% [markdown]
# ## Ejercicio 2 · Crear el agente
# Crea el modelo a mano: `GoogleModel(nombre, provider=GoogleProvider(api_key=...))`, y con él un `Agent` con tus propias instrucciones (rol, español, no inventar). Escribe `crear_agente_gemini`. Esta parte no usa red, así que se autocorrige siempre.
# %%
def crear_agente_gemini(nombre_modelo: str, instrucciones: str, api_key: str) -> Agent:
    # TODO: GoogleModel(nombre_modelo, provider=GoogleProvider(api_key=api_key)) y un Agent con instructions
    ...


MIS_INSTRUCCIONES = ""  # TODO: escribe tus instrucciones (rol, español, no inventes datos)
# %%
comprobar("Ejercicio 2 · crear el agente", lambda: isinstance(crear_agente_gemini(ajustes.gemini_model, "Hola", clave or "clave-de-prueba"), Agent) and MIS_INSTRUCCIONES.strip() != "", "crear_agente_gemini debe devolver un Agent y MIS_INSTRUCCIONES no puede estar vacía")
# %% [markdown]
# ## Ejercicio 3 · Errores amables
# Los errores de red son normales (cuota agotada, clave mal copiada). Completa `mensaje_error`: para un `ModelHTTPError` con `status_code` 429 debe hablar de la **cuota** y sugerir esperar o cambiar de modelo; con 400, 401 o 403, de la **clave**; con cualquier otro, mostrar el código. También se autocorrige sin red.
# %%
def mensaje_error(exc: ModelHTTPError) -> str:
    # TODO: 429 -> cuota; 400, 401 o 403 -> clave; otro -> el código
    return "TODO"


async def preguntar(agente: Agent, texto: str):
    """Ejecuta el agente; ante un error HTTP del proveedor imprime un mensaje amable y devuelve None."""
    try:
        return await agente.run(texto)
    except ModelHTTPError as exc:
        print("⚠️", mensaje_error(exc))
        return None
# %%
comprobar("Ejercicio 3 · errores amables", lambda: "cuota" in mensaje_error(ModelHTTPError(429, "m")).lower() and "clave" in mensaje_error(ModelHTTPError(403, "m")).lower() and "clave" in mensaje_error(ModelHTTPError(400, "m")).lower() and "500" in mensaje_error(ModelHTTPError(500, "m")), "429 debe mencionar la cuota; 400/403, la clave; otros, el código")
# %% [markdown]
# ## Ejercicio 4 · Una respuesta real
# Ejecuta de verdad: `r = await agente.run(...)`; muestra `r.output` y `r.usage`. Si falta la clave o estás en modo simulado, la celda te dice qué hacer y no rompe nada.
# %%
r = None
if LISTO_PARA_RED:
    agente_gemini = crear_agente_gemini(ajustes.gemini_model, MIS_INSTRUCCIONES, clave)
    r = await preguntar(agente_gemini, "En una frase: ¿qué debería llevar Alex a un taller en Tarata?")
    if r:
        print(r.output)
        print(r.usage)
else:
    print("Sin red: revisa el Ejercicio 1 (clave y COURSE_OFFLINE=0).")
# %%
comprobar("Ejercicio 4 · respuesta real de Gemini", lambda: r is not None and bool(r.output.strip()) and r.usage.requests >= 1, "Sin respuesta real: revisa la clave (Ejercicio 1), COURSE_OFFLINE=0 y reinicia el kernel; si viste 429, espera un minuto")
# %% [markdown]
# ## Ejercicio 5 · Compara dos modelos
# Misma pregunta, mismas instrucciones, dos modelos. Anota los tokens de entrada y salida de cada uno en `uso` (`r.usage.input_tokens`, `r.usage.output_tokens`). Luego escribe en `conclusion` una frase: ¿cuál gastó más tokens y por qué crees que fue? (Si un modelo da 429, espera y repite; si no existe para tu cuenta, cambia el nombre por otro modelo gratuito.)
# %%
MODELOS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
PREGUNTA = "Resume en tres puntos qué es un agente de IA."
uso: dict[str, tuple[int, int]] = {}
if LISTO_PARA_RED:
    for nombre in MODELOS:
        agente = crear_agente_gemini(nombre, MIS_INSTRUCCIONES, clave)
        res = await preguntar(agente, PREGUNTA)
        if res:
            pass  # TODO: guarda uso[nombre] = (tokens de entrada, tokens de salida)
    print(uso)
conclusion = ""  # TODO
# %%
comprobar("Ejercicio 5 · comparación de modelos", lambda: len(uso) == 2 and all(i > 0 and o > 0 for i, o in uso.values()) and len(conclusion.split()) >= 5, "Necesitas los tokens de los dos modelos (con red) y una conclusión de al menos 5 palabras")
# %% [markdown]
# El reto usa un modelo `Gasto` (el mismo del Ejercicio 11 de `03_ejercicios.ipynb`).
# %%
from typing import Literal

from pydantic import BaseModel, Field

Categoria = Literal["transporte", "comida", "taller", "otros"]


class Gasto(BaseModel):
    concepto: str = Field(min_length=1)
    monto: float = Field(gt=0)
    categoria: Categoria
    fecha: date
# %% [markdown]
# # Reto final (opcional, con IA real) · Del texto libre a un `Gasto`
# Pide al modelo configurado que convierta una frase libre en un `Gasto` validado usando `output_type`. Se ejecuta solo con IA real (`COURSE_OFFLINE=0`). Escribe tus instrucciones: dile cuál es «hoy» para que entienda «ayer».
# %%
from copiloto.agente import esquema_salida
from copiloto.config import crear_modelo

INSTRUCCIONES_RETO = ""  # TODO: extrae el gasto de la frase; indica la fecha de hoy y las categorías
gasto_reto = None
if not OFFLINE and clave:
    agente_reto = Agent(crear_modelo(settings, OFFLINE), instructions=INSTRUCCIONES_RETO, output_type=esquema_salida(settings, OFFLINE, tipo=Gasto))
    try:
        res = await agente_reto.run("Ayer gasté 35 Bs en micro a Quillacollo")
        gasto_reto = res.output
        print(gasto_reto)
    except ModelHTTPError as exc:
        print("⚠️", mensaje_error(exc))
else:
    print("Reto omitido: requiere IA real (ver el Ejercicio 1).")
# %%
revisar("Reto · gasto estructurado", lambda: gasto_reto is not None and gasto_reto.monto == 35 and gasto_reto.categoria == "transporte" and gasto_reto.fecha == date(2030, 5, 13), "Con IA real debe salir monto 35, categoría transporte y fecha 2030-05-13 (opcional)")
# %% [markdown]
# # Recuento
# %%
hechos = sum(RESULTADOS.values())
print(f"{hechos} de {len(RESULTADOS)} comprobaciones en ✅")
print("⏳ pendientes:", [n for n, ok in RESULTADOS.items() if not ok] or "ninguna")
# %% [markdown]
# ## Cómo entregar
# 1. Reinicia el kernel y ejecuta **todo** el notebook de arriba abajo (*Kernel → Restart and Run All*).
# 2. Comprueba el recuento: lo ideal es ver ✅ en los ejercicios 1 a 5 (el reto es opcional).
# 3. Guarda el notebook **con las salidas visibles** y súbelo donde indique el aula virtual (o muéstralo al inicio de la sesión 1). **Antes de subirlo**, comprueba que no se imprimió ninguna clave.
# 4. Si algo no sale (clave, cuota 429), entrega igual: cuéntanos en una celda de texto dónde te trabaste.
