# Fuente de notebook Jupyter con top-level await; regenerar con fuentes/generar_notebooks.py.
# ruff: noqa: F704
# %% [markdown]
# # Tarea S0 · Ejercicios de IA, Python y Pydantic
# **Pregunta:** ¿puedo escribir yo mismo el código que sostiene a un agente: estimar costos, controlar el contexto, validar datos y hablar con un modelo real?
# **Producto:** 13 ejercicios con autocorrección (✅/⏳) y un reto opcional, ambientados en el «Contexto de Alex»: agenda, gastos y el viaje a Tarata. Todos los datos son ficticios y «hoy» es el 2030-05-14.
# **Al terminar:** habrás practicado tokens, temperatura y ventana de contexto (Parte A); comprensiones, `dataclass`, errores, JSON, asincronía y choques de horario (Parte B); validación con Pydantic y esquema de una tool (Parte C); y habrás conectado Pydantic AI con tu propia clave gratuita de Gemini (Parte D).
# **Formato:** tarea autónoma de unas 2 a 3 h. Complementa a `00_repaso.ipynb` (no repite sus ejercicios). Se revisa al inicio de la sesión 1.
# **Cómo se usa:** completa cada celda marcada con `TODO` o `...` y ejecuta la celda `revisar(...)` que sigue. ⏳ significa «aún no», ✅ significa «correcto». Ninguna celda rompe el notebook si no la has hecho. Todo funciona sin red salvo la Parte D y el reto.
# %%
import asyncio
import json
import math
import random
import re
import time
from dataclasses import dataclass
from datetime import date

from copiloto.practica import preparar, revisar

settings, OFFLINE = preparar()
HOY = date(2030, 5, 14)
RESULTADOS: dict[str, bool] = {}


def comprobar(nombre: str, condicion, pista: str = "") -> None:
    """Como `revisar`, pero apunta el resultado para el recuento final."""
    RESULTADOS[nombre] = revisar(nombre, condicion, pista)
# %% [markdown]
# # Parte A · Introducción a la IA, con código
# %% [markdown]
# ## Ejercicio 1 · Tokens y costo de un prompt
# Los modelos cobran por **tokens**. Una regla práctica para español es `tokens ≈ palabras / 0.75` (redondeando hacia arriba). Escribe `estimar_tokens` y `costo_usd`. El costo es `tokens_entrada × precio_entrada + tokens_salida × precio_salida`, con precios dados **por millón de tokens**.
# %%
PRECIO_ENTRADA = 0.50  # USD por millón de tokens (ilustrativo)
PRECIO_SALIDA = 2.00  # USD por millón de tokens (ilustrativo)


def estimar_tokens(texto: str) -> int:
    # TODO: palabras / 0.75, redondeado hacia arriba (math.ceil)
    ...


def costo_usd(prompt: str, tokens_salida: int = 200) -> float:
    # TODO: usa estimar_tokens y los dos precios
    ...
# %%
comprobar("Ejercicio 1 · tokens", lambda: estimar_tokens("uno dos tres") == 4 and estimar_tokens("") == 0 and estimar_tokens("a b c d e f g h i") == 12, "9 palabras deben dar 12 tokens; texto vacío, 0")
comprobar("Ejercicio 1 · costo", lambda: math.isclose(costo_usd("palabra " * 3000), 0.0024), "3000 palabras = 4000 tokens de entrada y 200 de salida: 0,0024 USD")
# %% [markdown]
# ## Ejercicio 2 · Temperatura: elegir el siguiente token
# Dada una distribución de probabilidades, `siguiente_token` elige un token. Con `temperatura <= 0` devuelve el más probable (argmax). Con temperatura positiva, reajusta cada probabilidad como `p ** (1 / temperatura)` y **muestrea** con `random.Random(semilla).choices(...)`. Así la misma semilla da siempre la misma elección.
# %%
PROBS = {"10:00": 0.60, "11:00": 0.25, "mañana": 0.10, "tres": 0.05}  # siguiente token tras «Reunión a las»


def siguiente_token(probs: dict[str, float], temperatura: float, semilla: int = 0) -> str:
    # TODO: argmax si temperatura <= 0; si no, muestreo con pesos p ** (1 / temperatura)
    ...
# %%
comprobar("Ejercicio 2 · T=0 es argmax", lambda: all(siguiente_token(PROBS, 0, s) == "10:00" for s in range(10)), "Con temperatura 0 siempre debe salir «10:00»")
comprobar("Ejercicio 2 · misma semilla, mismo resultado", lambda: siguiente_token(PROBS, 1.0, 7) == siguiente_token(PROBS, 1.0, 7), "Usa random.Random(semilla), no el generador global")
comprobar("Ejercicio 2 · T alta da variedad", lambda: len({siguiente_token(PROBS, 5.0, s) for s in range(60)}) >= 3 and {siguiente_token(PROBS, 0.05, s) for s in range(60)} == {"10:00"}, "T=5 debe dar al menos 3 tokens distintos; T=0.05, solo «10:00»")
# %% [markdown]
# ## Ejercicio 3 · ¿Predictiva, generativa o agéntica?
# Clasifica cada caso con `"predictiva"`, `"generativa"` o `"agentica"`. Pista: la **predictiva** estima o clasifica; la **generativa** produce contenido nuevo; la **agéntica** decide pasos y usa herramientas para actuar hacia un objetivo.
# %%
CASOS = {
    1: "Un modelo estima si un cliente dejará de pagar su crédito.",
    2: "Un asistente redacta un correo de disculpa para Ana a partir de tres ideas sueltas.",
    3: "Un asistente revisa la agenda, detecta un choque, propone mover la reunión y, con tu aprobación, crea el evento.",
    4: "Un filtro marca un correo como spam.",
    5: "Un sistema crea una imagen para el afiche del taller en Tarata.",
    6: "Un programa consulta el clima, compara dos pasajes y arma el itinerario a Tarata llamando herramientas hasta terminar.",
}
respuestas = {1: "...", 2: "...", 3: "...", 4: "...", 5: "...", 6: "..."}  # TODO
# %%
ESPERADO = {1: "predictiva", 2: "generativa", 3: "agentica", 4: "predictiva", 5: "generativa", 6: "agentica"}
aciertos = sum(respuestas.get(k) == v for k, v in ESPERADO.items())
comprobar("Ejercicio 3 · clasificación", lambda: aciertos == 6, f"{aciertos} de 6 correctos")
# %% [markdown]
# ## Ejercicio 4 · Ventana de contexto: recortar el historial
# Un modelo solo «ve» `N` tokens. Escribe `recortar_historial(mensajes, max_tokens)`: conserva **siempre el primer mensaje** (el de sistema) y, de los demás, los **más recientes que quepan** (sin dejar huecos en medio). Cuenta los tokens con `estimar_tokens(m["content"])`. No modifiques la lista original.
# %%
HISTORIAL = [
    {"role": "system", "content": "Eres Mi copiloto, asistente de Alex."},
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "Hola Alex, ¿en qué te ayudo hoy?"},
    {"role": "user", "content": "Agenda de mañana por favor"},
    {"role": "assistant", "content": "Tienes taller a las 10:00 y viaje"},
]


def recortar_historial(mensajes: list[dict], max_tokens: int) -> list[dict]:
    # TODO: sistema + los mensajes más recientes que quepan (recorre el resto al revés)
    ...
# %%
comprobar("Ejercicio 4 · todo cabe", lambda: recortar_historial(HISTORIAL, 1000) == HISTORIAL, "Con un límite enorme debe devolver todo")
comprobar("Ejercicio 4 · recorta lo antiguo", lambda: recortar_historial(HISTORIAL, 30) == [HISTORIAL[0], HISTORIAL[3], HISTORIAL[4]], "Con 30 tokens deben quedar el sistema y los dos últimos")
comprobar("Ejercicio 4 · solo el sistema", lambda: recortar_historial(HISTORIAL, 9) == [HISTORIAL[0]], "Si nada más cabe, queda solo el mensaje de sistema")
# %% [markdown]
# # Parte B · Python para agentes
# %% [markdown]
# ## Ejercicio 5 · Agenda del día con comprensiones
# Escribe `agenda_del_dia(eventos, desde="00:00")`: un diccionario `{hora: titulo}` **ordenado por hora**, solo con los eventos cuya hora sea `>= desde`. Usa una comprensión de diccionario y `sorted`. (Las horas «HH:MM» se comparan bien como texto.)
# %%
EVENTOS = [
    {"hora": "15:30", "titulo": "Llamar a Ana"},
    {"hora": "09:00", "titulo": "Taller en Tarata"},
    {"hora": "12:30", "titulo": "Almuerzo con el equipo"},
    {"hora": "08:00", "titulo": "Revisar correo"},
]


def agenda_del_dia(eventos: list[dict], desde: str = "00:00") -> dict[str, str]:
    # TODO: comprensión de diccionario sobre eventos ordenados por hora, filtrando por `desde`
    ...
# %%
comprobar("Ejercicio 5 · ordenada", lambda: list(agenda_del_dia(EVENTOS)) == ["08:00", "09:00", "12:30", "15:30"], "Las horas deben salir en orden")
comprobar("Ejercicio 5 · filtro", lambda: agenda_del_dia(EVENTOS, "12:00") == {"12:30": "Almuerzo con el equipo", "15:30": "Llamar a Ana"}, "Con desde='12:00' quedan dos eventos")
# %% [markdown]
# ## Ejercicio 6 · Un `dataclass` con prioridad
# Completa `Tarea`: `titulo`, `prioridad` (1 = alta, 2 = media, 3 = baja; por defecto 3) y `hecha` (por defecto `False`). Añade el método `urgente()` (prioridad 1 y no hecha) y `marcar_hecha()`. Si la prioridad no está entre 1 y 3, lanza `ValueError` en `__post_init__`. Luego escribe `ordenar(tareas)`: por prioridad y, a igual prioridad, por título.
# %%
@dataclass
class Tarea:
    titulo: str
    # TODO: prioridad (int, por defecto 3) y hecha (bool, por defecto False)
    # TODO: __post_init__ que valide la prioridad; métodos urgente() y marcar_hecha()


def ordenar(tareas: list[Tarea]) -> list[Tarea]:
    # TODO
    ...
# %%
def _prueba_tarea() -> bool:
    t = Tarea("Comprar pasajes", prioridad=1)
    ok = t.urgente() and not Tarea("Leer").urgente()
    t.marcar_hecha()
    ok = ok and not t.urgente() and Tarea("x").prioridad == 3
    nombres = [x.titulo for x in ordenar([Tarea("b", 2), Tarea("z", 1), Tarea("a", 2)])]
    return ok and nombres == ["z", "a", "b"]


def _prioridad_invalida() -> bool:
    try:
        Tarea("x", prioridad=9)
    except ValueError:
        return True
    return False


comprobar("Ejercicio 6 · métodos y orden", _prueba_tarea, "Revisa urgente(), marcar_hecha(), el valor por defecto y ordenar()")
comprobar("Ejercicio 6 · prioridad inválida", _prioridad_invalida, "Tarea('x', prioridad=9) debe lanzar ValueError")
# %% [markdown]
# ## Ejercicio 7 · Errores con mensajes útiles
# El modelo (o la persona) escribe «3 horas a 40 Bs» y tu código debe entenderlo. Escribe `presupuesto(texto)` que devuelva `horas × tarifa`. Acepta coma decimal («1,5 horas a 40 Bs»). Si el texto no tiene ese formato, o las horas no son mayores que 0, lanza `ValueError` con un mensaje que **incluya el texto recibido** y explique el formato esperado. Pista: `re.fullmatch` con `re.IGNORECASE`.
# %%
def presupuesto(texto: str) -> float:
    # TODO: extrae horas y tarifa con una expresión regular; lanza ValueError con mensaje útil
    ...
# %%
def _lanza(texto: str) -> bool:
    try:
        presupuesto(texto)
    except ValueError as exc:
        return texto in str(exc)
    return False


comprobar("Ejercicio 7 · casos válidos", lambda: presupuesto("3 horas a 40 Bs") == 120 and presupuesto("1,5 horas a 40 Bs") == 60 and presupuesto("1 hora a 25 bs") == 25, "«3 horas a 40 Bs» = 120; «1,5 horas a 40 Bs» = 60")
comprobar("Ejercicio 7 · errores útiles", lambda: _lanza("tres horas") and _lanza("0 horas a 40 Bs"), "Debe lanzar ValueError y citar el texto recibido en el mensaje")
# %% [markdown]
# ## Ejercicio 8 · JSON y un despachador con lista blanca
# Un modelo pide una herramienta con un mensaje JSON como `{"tool": "sumar_gastos", "args": {"montos": [35, 20]}}`. Escribe `ejecutar(mensaje_json)`, que **nunca lanza excepciones** y devuelve siempre un texto JSON: `{"tool": ..., "resultado": ...}` si todo salió bien o `{"error": "..."}` si el JSON es inválido, la tool **no está en la lista blanca** (`TOOLS`) o los argumentos no corresponden. Es el germen del bucle de la sesión 1.
# %%
def sumar_gastos(montos: list[float]) -> float:
    return sum(montos)


def dias_hasta(fecha: str) -> int:
    return (date.fromisoformat(fecha) - HOY).days


def borrar_todo() -> str:  # existe, pero NO debe poder pedirla el modelo
    return "borrado"


TOOLS = {"sumar_gastos": sumar_gastos, "dias_hasta": dias_hasta}


def ejecutar(mensaje_json: str) -> str:
    # TODO: json.loads, comprobar la lista blanca, llamar con **args, y capturar los errores
    ...
# %%
def _ok() -> bool:
    msg = json.dumps({"tool": "sumar_gastos", "args": {"montos": [35, 20]}})
    s = json.loads(ejecutar(msg))
    d = json.loads(ejecutar(json.dumps({"tool": "dias_hasta", "args": {"fecha": "2030-05-20"}})))
    return s == {"tool": "sumar_gastos", "resultado": 55} and d["resultado"] == 6


comprobar("Ejercicio 8 · tools válidas", _ok, "sumar_gastos([35, 20]) = 55 y dias_hasta('2030-05-20') = 6")
comprobar("Ejercicio 8 · lista blanca", lambda: "error" in json.loads(ejecutar('{"tool": "borrar_todo", "args": {}}')), "«borrar_todo» no está en TOOLS: debe devolver un error")
comprobar("Ejercicio 8 · entradas rotas", lambda: all("error" in json.loads(ejecutar(m)) for m in ("esto no es json", '{"args": {}}', '{"tool": "dias_hasta", "args": {"dia": 1}}', '{"tool": "dias_hasta", "args": {"fecha": "ayer"}}')), "JSON inválido, sin «tool», argumentos erróneos o fecha mala: siempre un error, nunca una excepción")
# %% [markdown]
# ## Ejercicio 9 · Choques de horario
# Dos eventos chocan si se **solapan** (tocarse en el borde, como terminar a las 11:30 y empezar a las 11:30, no es choque). Escribe `choques(eventos)`: la lista de pares `(titulo_a, titulo_b)` que chocan, probando cada par una sola vez (`itertools.combinations`).
# %%
from itertools import combinations

AGENDA = [
    {"titulo": "Taller", "inicio": "09:00", "fin": "11:00"},
    {"titulo": "Reunión con Ana", "inicio": "10:30", "fin": "11:30"},
    {"titulo": "Llamada", "inicio": "11:30", "fin": "12:00"},
    {"titulo": "Almuerzo", "inicio": "12:00", "fin": "13:00"},
    {"titulo": "Viaje", "inicio": "12:30", "fin": "14:00"},
]


def choques(eventos: list[dict]) -> list[tuple[str, str]]:
    # TODO: dos eventos se solapan si a.inicio < b.fin y b.inicio < a.fin
    ...
# %%
comprobar("Ejercicio 9 · choques", lambda: choques(AGENDA) == [("Taller", "Reunión con Ana"), ("Almuerzo", "Viaje")], "Deben chocar Taller con Reunión y Almuerzo con Viaje; «Llamada» solo toca los bordes")
comprobar("Ejercicio 9 · sin choques", lambda: choques(AGENDA[2:3]) == [] and choques([]) == [], "Con uno o ningún evento no hay choques")
# %% [markdown]
# ## Ejercicio 10 · Varias llamadas a la vez con `asyncio.gather`
# Las tools de un agente esperan a la red. Tres consultas de 0,5 s en secuencia tardan 1,5 s; en paralelo, 0,5 s. La celda de abajo las hace **en secuencia**: cámbiala para que corran **a la vez** con `asyncio.gather` y devuelve también los segundos que tardó. (En Jupyter se puede usar `await` directamente en una celda.)
# %%
async def consultar_clima(ciudad: str) -> str:
    await asyncio.sleep(0.5)
    return f"{ciudad}: 18 °C"


async def consultar_cambio() -> str:
    await asyncio.sleep(0.5)
    return "1 USD = 6,96 Bs"


async def consultar_feriados() -> str:
    await asyncio.sleep(0.5)
    return "Sin feriados esta semana"


async def consultar_todo() -> tuple[list[str], float]:
    inicio = time.perf_counter()
    # TODO: ahora van una tras otra; usa asyncio.gather para que corran a la vez
    resultados = [await consultar_clima("Tarata"), await consultar_cambio(), await consultar_feriados()]
    return resultados, time.perf_counter() - inicio


resultados_async, segundos = await consultar_todo()
print(f"{len(resultados_async)} respuestas en {segundos:.2f} s")
# %%
comprobar("Ejercicio 10 · en paralelo", lambda: len(resultados_async) == 3 and segundos < 1.0, f"Tardó {segundos:.2f} s; en paralelo debe ser menos de 1 s")
# %% [markdown]
# # Parte C · Pydantic
# %% [markdown]
# ## Ejercicio 11 · Un modelo `Gasto` con validación
# Completa `Gasto`: `concepto` (texto no vacío), `monto` (**mayor que 0**), `categoria` (solo `"transporte"`, `"comida"`, `"taller"` u `"otros"`) y `fecha` (`datetime.date`). Después escribe `leer_gastos(texto_json)`, que recibe una lista JSON y devuelve `(validos, n_errores)`: cada elemento que no valide suma un error (`ValidationError`) en lugar de detener todo.
# %%
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

Categoria = Literal["transporte", "comida", "taller", "otros"]


class Gasto(BaseModel):
    concepto: str
    monto: float  # TODO: mayor que 0 (Field(gt=0))
    categoria: str  # TODO: Categoria (el Literal de arriba)
    fecha: date
    # TODO: concepto no vacío (Field(min_length=1))


GASTOS_JSON = """[
  {"concepto": "Micro a Quillacollo", "monto": 35, "categoria": "transporte", "fecha": "2030-05-13"},
  {"concepto": "Almuerzo del taller", "monto": 60.5, "categoria": "comida", "fecha": "2030-05-13"},
  {"concepto": "Refrigerio", "monto": 0, "categoria": "comida", "fecha": "2030-05-14"},
  {"concepto": "Impresiones", "monto": 12, "categoria": "diversión", "fecha": "2030-05-14"},
  {"concepto": "Pasaje a Tarata", "monto": 25, "categoria": "transporte", "fecha": "2030-05-14"}
]"""


def leer_gastos(texto_json: str) -> tuple[list[Gasto], int]:
    # TODO: recorre json.loads(texto_json); valida cada uno con Gasto.model_validate;
    # captura ValidationError y cuéntalo (imprime exc.errors() para leer los motivos)
    ...
# %%
def _rechaza(**campos) -> bool:
    base = {"concepto": "x", "monto": 1, "categoria": "otros", "fecha": "2030-05-14"}
    try:
        Gasto(**{**base, **campos})
    except ValidationError:
        return True
    return False


comprobar("Ejercicio 11 · Gasto válido", lambda: Gasto(concepto="Micro", monto=35, categoria="transporte", fecha="2030-05-13").fecha == date(2030, 5, 13), "Un gasto correcto debe construirse (la fecha en texto ISO se convierte a date)")
comprobar("Ejercicio 11 · rechaza lo inválido", lambda: _rechaza(monto=0) and _rechaza(monto=-5) and _rechaza(categoria="diversión") and _rechaza(concepto=""), "Monto <= 0, categoría fuera del Literal y concepto vacío deben fallar")
comprobar("Ejercicio 11 · leer_gastos", lambda: (lambda r: len(r[0]) == 3 and r[1] == 2)(leer_gastos(GASTOS_JSON)), "De los 5 elementos, 3 son válidos y 2 fallan (monto 0 y categoría «diversión»)")
# %% [markdown]
# ## Ejercicio 12 · El esquema que ve el modelo
# El modelo **no ve tu código Python**: ve el **esquema JSON** de cada tool. Pydantic AI lo deriva de la firma y de la docstring. Obtén el esquema de `registrar_gasto` con `Tool(registrar_gasto).function_schema.json_schema` y guárdalo en `esquema`. Luego responde en `respuesta_requeridos` qué parámetros son obligatorios (lista de nombres).
# %%
from pydantic_ai.tools import Tool


def registrar_gasto(concepto: str, monto: float, categoria: Categoria = "otros") -> str:
    """Registra un gasto de Alex (datos ficticios)."""
    return f"Registrado: {concepto} por {monto} Bs"


esquema = {}  # TODO: Tool(registrar_gasto).function_schema.json_schema
respuesta_requeridos = []  # TODO: ¿qué parámetros son obligatorios?
print(json.dumps(esquema, ensure_ascii=False, indent=1))
# %%
comprobar("Ejercicio 12 · esquema de la tool", lambda: set(esquema["properties"]) == {"concepto", "monto", "categoria"} and esquema["properties"]["categoria"]["enum"] == ["transporte", "comida", "taller", "otros"], "Debe tener concepto, monto y categoria, esta última con su enum")
comprobar("Ejercicio 12 · obligatorios", lambda: sorted(respuesta_requeridos) == ["concepto", "monto"], "categoria tiene valor por defecto, así que no es obligatoria")
# %% [markdown]
# # Parte D · Conexión con Pydantic AI y tu clave gratuita de Gemini
# Hasta aquí todo fue sin red. Ahora hablas con un modelo **real**. Necesitas una clave **gratuita** de Google AI Studio (sin tarjeta; no vincules facturación). Si aún no la tienes: `uv run copiloto-configurar --ruta gemini` te la pide sin mostrarla y la guarda en `.env`; o créala en https://aistudio.google.com/apikey. Para usarla pon además `COURSE_OFFLINE=0` en `.env` (el configurador ya lo hace) y reinicia el kernel. **Nunca** pegues la clave en el notebook ni la subas a GitHub. Usa solo datos ficticios.
# %% [markdown]
# ## Ejercicio 13 · Tu primer agente con Gemini
# **Paso 1.** Comprueba la configuración **sin imprimir la clave** (solo si existe y cuántos caracteres tiene). Ejecuta la celda tal cual.
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
# **Paso 2.** Crea el modelo a mano: `GoogleModel(nombre, provider=GoogleProvider(api_key=...))`, y con él un `Agent` con tus propias instrucciones (rol, español, no inventar). Escribe `crear_agente_gemini`. Esta parte no usa red, así que se autocorrige siempre.
# %%
def crear_agente_gemini(nombre_modelo: str, instrucciones: str, api_key: str) -> Agent:
    # TODO: GoogleModel(nombre_modelo, provider=GoogleProvider(api_key=api_key)) y un Agent con instructions
    ...


MIS_INSTRUCCIONES = ""  # TODO: escribe tus instrucciones (rol, español, no inventes datos)
# %%
comprobar("Ejercicio 13 · crear el agente", lambda: isinstance(crear_agente_gemini(ajustes.gemini_model, "Hola", clave or "clave-de-prueba"), Agent) and MIS_INSTRUCCIONES.strip() != "", "crear_agente_gemini debe devolver un Agent y MIS_INSTRUCCIONES no puede estar vacía")
# %% [markdown]
# **Paso 3.** Los errores de red son normales (cuota agotada, clave mal copiada). Completa `mensaje_error`: para un `ModelHTTPError` con `status_code` 429 debe hablar de la **cuota** y sugerir esperar o cambiar de modelo; con 400, 401 o 403, de la **clave**; con cualquier otro, mostrar el código. También se autocorrige sin red.
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
comprobar("Ejercicio 13 · errores amables", lambda: "cuota" in mensaje_error(ModelHTTPError(429, "m")).lower() and "clave" in mensaje_error(ModelHTTPError(403, "m")).lower() and "clave" in mensaje_error(ModelHTTPError(400, "m")).lower() and "500" in mensaje_error(ModelHTTPError(500, "m")), "429 debe mencionar la cuota; 400/403, la clave; otros, el código")
# %% [markdown]
# **Paso 4.** Ejecuta de verdad: `r = await agente.run(...)`; muestra `r.output` y `r.usage`. Si falta la clave o estás en modo simulado, la celda te dice qué hacer y no rompe nada.
# %%
r = None
if LISTO_PARA_RED:
    agente_gemini = crear_agente_gemini(ajustes.gemini_model, MIS_INSTRUCCIONES, clave)
    r = await preguntar(agente_gemini, "En una frase: ¿qué debería llevar Alex a un taller en Tarata?")
    if r:
        print(r.output)
        print(r.usage)
else:
    print("Sin red: revisa el Paso 1 (clave y COURSE_OFFLINE=0).")
# %%
comprobar("Ejercicio 13 · respuesta real de Gemini", lambda: r is not None and bool(r.output.strip()) and r.usage.requests >= 1, "Sin respuesta real: revisa la clave (Paso 1), COURSE_OFFLINE=0 y reinicia el kernel; si viste 429, espera un minuto")
# %% [markdown]
# **Paso 5. Compara dos modelos.** Misma pregunta, mismas instrucciones, dos modelos. Anota los tokens de entrada y salida de cada uno en `uso` (`r.usage.input_tokens`, `r.usage.output_tokens`). Luego escribe en `conclusion` una frase: ¿cuál gastó más tokens y por qué crees que fue? (Si un modelo da 429, espera y repite; si no existe para tu cuenta, cambia el nombre por otro modelo gratuito.)
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
comprobar("Ejercicio 13 · comparación de modelos", lambda: len(uso) == 2 and all(i > 0 and o > 0 for i, o in uso.values()) and len(conclusion.split()) >= 5, "Necesitas los tokens de los dos modelos (con red) y una conclusión de al menos 5 palabras")
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
    print("Reto omitido: requiere IA real (ver el inicio de la Parte D).")
# %%
revisar("Reto · gasto estructurado", lambda: gasto_reto is not None and gasto_reto.monto == 35 and gasto_reto.categoria == "transporte" and gasto_reto.fecha == date(2030, 5, 13), "Con IA real debe salir monto 35, categoría transporte y fecha 2030-05-13 (opcional)")
# %% [markdown]
# # Recuento y autoevaluación
# %%
hechos = sum(RESULTADOS.values())
print(f"{hechos} de {len(RESULTADOS)} comprobaciones en ✅")
print("⏳ pendientes:", [n for n, ok in RESULTADOS.items() if not ok] or "ninguna")
# %% [markdown]
# **Autoevaluación (responde en una celda de texto, 2 a 3 líneas cada una):**
# 1. ¿Por qué una temperatura alta hace menos útil a un agente que ejecuta acciones?
# 2. ¿Qué pasa con la parte vieja de la conversación cuando recortas el historial? ¿Qué riesgo tiene?
# 3. ¿Por qué el despachador usa una lista blanca en vez de llamar a cualquier función que pida el modelo?
# 4. ¿Qué diferencia hay entre que Python rechace un `monto` negativo y que lo rechace Pydantic?
# 5. ¿Qué ve exactamente el modelo de una tool: tu código o su esquema JSON?
# %% [markdown]
# ## Cómo entregar
# 1. Reinicia el kernel y ejecuta **todo** el notebook de arriba abajo (*Kernel → Restart and Run All*).
# 2. Comprueba el recuento final: lo ideal es ver ✅ en todos los ejercicios 1 a 13 (el reto es opcional).
# 3. Guarda el notebook **con las salidas visibles** y súbelo donde indique el aula virtual (o muéstralo al inicio de la sesión 1: se revisa ahí). **Antes de subirlo**, comprueba que no se imprimió ninguna clave.
# 4. Si algo no sale, entrega igual: cuéntanos en una celda de texto dónde te trabaste. Eso orienta el repaso de 10 minutos.
