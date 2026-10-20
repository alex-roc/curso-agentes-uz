# Fuente de notebook Jupyter con top-level await; regenerar con fuentes/generar_notebooks.py.
# ruff: noqa: F704
# %% [markdown]
# # 0 · Repaso previo: introducción a la IA y Python para agentes
# **Pregunta:** ¿qué tipo de IA vamos a construir y qué necesito dominar de Python para leer sin tropiezos el código de Mi copiloto?
# **Producto:** seis ejercicios cortos con autocorrección: un clasificador de tipos de IA (parte 1) y, en la parte 2, un dataclass, una función async, un modelo Pydantic con validador, la lectura de un esquema JSON y una configuración con secretos.
# **Al terminar:** podrás explicar qué hace la temperatura, por qué los tokens importan y en qué se diferencian la IA predictiva, la generativa y la agéntica; además, podrás levantar el entorno con uv, escribir funciones con tipos, esperar varias llamadas a la vez con `asyncio.gather`, validar datos con Pydantic y explicar por qué un secreto nunca se imprime.
# **Formato:** autoestudio de unas 4 h en total (este notebook: parte 1, unos 30 min; parte 2, unos 75 min), parte de las 12 h autónomas del curso. Todo se ejecuta sin red ni LLM. En la sesión 1 dedicamos 10 minutos a repasar lo que te trabó.
# %% [markdown]
# ## Preparación reproducible
# Instala las dependencias **antes** de abrir el notebook (`uv sync`, ver el README del repositorio). Las celdas no instalan paquetes.
# Este repaso no usa un modelo de lenguaje: `COURSE_OFFLINE=1` solo decide qué mensaje imprime `preparar()`. Las funciones de clima y tipo de cambio usan respuestas guardadas (fixtures) en lugar de internet.
# %%
from copiloto.practica import preparar, revisar, ver_mensajes  # noqa: F401

settings, OFFLINE = preparar()
# %% [markdown]
# # Parte 1 · Introducción a la IA
# Antes de programar agentes conviene tener claro qué hace un modelo de lenguaje y qué tipo de IA vamos a construir. Esta parte no usa red ni modelos: simula el mecanismo con números ilustrativos. Acompaña a la primera parte de la exposición.
# %% [markdown]
# ## 1 · El modelo solo predice: temperatura y muestreo
# Un modelo de lenguaje calcula, para cada paso, una **puntuación por cada token posible**. Con `temperatura = 0` se elige siempre el más probable; con una temperatura mayor se **muestrea** y aparece variedad. Los números de abajo son ilustrativos: sirven para sentir el mecanismo, no para medir un modelo real.
# En el curso usamos `temperature=0` para el modelo local (`crear_modelo`, en `config.py`): queremos respuestas lo más repetibles posible al comparar.
# %%
import math
import random

# Puntuaciones ILUSTRATIVAS del siguiente token tras «Alex tiene reunión a las»
logits = {"09:00": 2.0, "10:00": 1.4, "mañana": 0.4, "tres": -0.5}


def muestrear(logits: dict[str, float], temperatura: float, semilla: int) -> str:
    if temperatura == 0:
        return max(logits, key=logits.get)  # voraz: siempre el más probable
    pesos = [math.exp(v / temperatura) for v in logits.values()]
    return random.Random(semilla).choices(list(logits), weights=pesos)[0]


for t in (0, 0.7, 2.0):
    print(f"T={t}:", [muestrear(logits, t, semilla=s) for s in range(8)])
# %% [markdown]
# Con `T=0` todas las muestras coinciden; con `T=2` aparecen opciones poco probables como «tres». Una temperatura alta no hace «más creativo» al agente: lo hace **menos predecible**, y un agente que ejecuta acciones necesita ser predecible.
# %% [markdown]
# ## 2 · Tokens: el modelo no ve letras
# El modelo trabaja con **tokens**, fragmentos de texto convertidos en números. Cada modelo tokeniza distinto, así que aquí solo **estimamos**: una regla práctica en inglés es ~4 caracteres por token; en español suele haber algo más de tokens por palabra. Para contar de verdad, usa el tokenizador del proveedor (por ejemplo https://tiktokenizer.vercel.app).
# Los tokens importan porque la ventana de contexto y el costo se miden en tokens: instrucciones, historial y resultados de herramientas compiten por el mismo espacio.
# %%
TEXTOS = {
    "pregunta": "¿Qué reuniones tengo mañana?",
    "instrucciones": "Eres Mi copiloto, el asistente personal de Alex. Responde en español, breve.",
    "correo": "Hola Alex, ¿podemos reunirnos esta semana para revisar el presupuesto del taller en Tarata? Ana",
}


def tokens_aproximados(texto: str) -> int:
    """Estimación gruesa: ~4 caracteres por token. No reemplaza al tokenizador real."""
    return max(1, round(len(texto) / 4))


for nombre, texto in TEXTOS.items():
    print(f"{nombre:13} {len(texto.split()):3} palabras · {len(texto):4} caracteres · ~{tokens_aproximados(texto)} tokens")
# %% [markdown]
# ## 3 · Predictiva, generativa o agéntica
# Tres maneras de usar modelos, según lo que producen:
#
# | Tipo | Produce | Quién decide el siguiente paso | Ejemplo con Alex |
# |---|---|---|---|
# | Predictiva | Una etiqueta o un número | El programa | «Este correo es importante» |
# | Generativa | Contenido nuevo (texto, imagen, audio) | La persona que pide | «Resume el correo de Ana» |
# | Agéntica | Acciones con herramientas, hacia un objetivo | El modelo, dentro de límites | «Busca un hueco y propón la reunión con Ana» |
#
# Lo que distingue a un agente no es que «hable mejor», sino que **usa herramientas** y **decide sus pasos** en un bucle.
# %% [markdown]
# ## Ejercicio 1 · ¿Qué tipo de IA es?
# Escribe `tipo_de_ia(salida, usa_herramientas, decide_pasos)` que devuelva `"predictiva"`, `"generativa"` o `"agentica"`:
# - Si el sistema **usa herramientas y decide sus pasos**, es `"agentica"`.
# - Si no, y su salida es contenido nuevo (`"texto"`, `"imagen"` o `"audio"`), es `"generativa"`.
# - En otro caso (`"etiqueta"` o `"numero"`), es `"predictiva"`.
#
# Luego se prueba con ocho casos reales del contexto de Alex.
# %%
from typing import Literal

TipoIA = Literal["predictiva", "generativa", "agentica"]


# TODO: aplica las tres reglas en ese orden (primero la agéntica).
def tipo_de_ia(salida: str, usa_herramientas: bool, decide_pasos: bool) -> TipoIA:
    return "predictiva"
# %%
# (descripción, salida, usa_herramientas, decide_pasos, tipo esperado)
CASOS = [
    ("Marcar un correo como spam o no spam", "etiqueta", False, False, "predictiva"),
    ("Estimar cuánto gastará Alex en junio", "numero", False, False, "predictiva"),
    ("Recomendar la siguiente canción", "etiqueta", False, False, "predictiva"),
    ("Resumir el correo de Ana", "texto", False, False, "generativa"),
    ("Generar una imagen para la invitación del taller", "imagen", False, False, "generativa"),
    ("Leer en voz alta el resumen del día", "audio", False, False, "generativa"),
    ("Revisar la agenda y proponer una hora para la reunión", "texto", True, True, "agentica"),
    ("Consultar el clima y los feriados y armar el plan del viaje", "texto", True, True, "agentica"),
]
for descripcion, salida, herramientas, pasos, _ in CASOS:
    print(f"{tipo_de_ia(salida, herramientas, pasos):10} ← {descripcion}")

revisar("Ejercicio 1 · tres casos predictivos", lambda: all(tipo_de_ia(*c[1:4]) == c[4] for c in CASOS if c[4] == "predictiva"), "Una etiqueta o un número sin herramientas es predictiva")
revisar("Ejercicio 1 · tres casos generativos", lambda: all(tipo_de_ia(*c[1:4]) == c[4] for c in CASOS if c[4] == "generativa"), "Texto, imagen o audio nuevos son generativa")
revisar("Ejercicio 1 · dos casos agénticos", lambda: all(tipo_de_ia(*c[1:4]) == c[4] for c in CASOS if c[4] == "agentica"), "Herramientas + decide sus pasos = agentica")
revisar("Ejercicio 1 · generar texto no basta para ser agente", lambda: tipo_de_ia("texto", False, True) == "generativa", "Sin herramientas no hay agente, aunque escriba muy bien")
# %% [markdown]
# Fíjate en el último caso: un sistema que escribe muy bien pero no usa herramientas sigue siendo generativo. En la sesión 1 le daremos al modelo un bucle y, en la sesión 2, herramientas: ahí empieza lo agéntico.
# %% [markdown]
# # Parte 2 · Python para agentes
# Entorno, uv, Python con tipos, async, httpx, Pydantic y secretos: el Python que usa el código de Mi copiloto. Desde aquí necesitas el entorno instalado (README del repositorio).
# %% [markdown]
# ## 4 · Entorno: ¿estoy en el Python del proyecto?
# El error más común de la primera semana es ejecutar el notebook con **otro** Python (el del sistema o el de Anaconda). `uv sync` crea la carpeta `.venv` en la raíz del repositorio y el kernel debe apuntar ahí.
# %%
import sys
from pathlib import Path

entorno = Path(sys.executable).parents[1].name
print("Python:", sys.version.split()[0])
print("Entorno del kernel:", entorno)
print("¿Es el .venv del proyecto?", entorno == ".venv")
# %% [markdown]
# Si imprime `False`, cierra Jupyter y ábrelo con `uv run jupyter lab` desde la carpeta que contiene `pyproject.toml`. Después elige el kernel el kernel «Python 3 (ipykernel)» del proyecto.
# %% [markdown]
# ## 5 · Python con tipos
# Los tipos no cambian lo que hace el programa: documentan qué espera cada función y permiten que Pydantic AI genere el esquema de una tool a partir de la firma. Usamos la sintaxis moderna: `str | None`, `list[dict]`, `Literal`.
# %%
from typing import Literal

# Datos ficticios: la agenda de Alex (hoy es el martes 14 de mayo de 2030 en el curso).
AGENDA = [
    {"fecha": "2030-05-14", "inicio": "09:00", "fin": "10:00", "titulo": "Reunión de proyecto", "tipo": "trabajo"},
    {"fecha": "2030-05-14", "inicio": "12:30", "fin": "13:30", "titulo": "Almuerzo", "tipo": "personal"},
    {"fecha": "2030-05-14", "inicio": "18:00", "fin": "19:00", "titulo": "Caminata", "tipo": "personal"},
    {"fecha": "2030-05-15", "inicio": "10:00", "fin": "11:00", "titulo": "Clase de Python", "tipo": "aprendizaje"},
]


def consultar_agenda(fecha: str) -> list[dict]:
    """Eventos ficticios de una fecha AAAA-MM-DD. Cada uno cita su fuente."""
    return [{**e, "fuente": f"agenda:{i}"} for i, e in enumerate(AGENDA) if e["fecha"] == fecha]


Turno = Literal["mañana", "tarde"]


def eventos_del_turno(fecha: str, turno: Turno, tipo: str | None = None) -> list[dict]:
    """Eventos de un día que empiezan antes (mañana) o después (tarde) de las 13:00."""
    eventos = consultar_agenda(fecha)
    elegidos = [e for e in eventos if (e["inicio"] < "13:00") == (turno == "mañana")]
    if tipo is not None:
        elegidos = [e for e in elegidos if e["tipo"] == tipo]
    return elegidos


for e in eventos_del_turno("2030-05-14", "tarde", tipo="personal"):
    print(f"{e['inicio']}-{e['fin']} · {e['titulo']} ({e['fuente']})")
# %% [markdown]
# Observa tres modismos que verás en todo el repositorio: un **f-string** con expresiones dentro de `{}`, una **comprensión de listas** para filtrar y un diccionario como registro (`e["titulo"]`). Los tipos de la firma son una promesa que tú y tu editor revisan; Python no los impone al ejecutar. Pydantic sí los impone.
# %% [markdown]
# ## 6 · Dataclasses
# Una `dataclass` es una clase pensada para guardar datos: genera `__init__`, `__repr__` y la comparación por igualdad a partir de los campos anotados.
# %%
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Reunion:
    titulo: str
    inicio: str
    fin: str


reunion = Reunion("Revisión del proyecto", "10:00", "11:00")
print(reunion)
print(asdict(reunion))
print(reunion == Reunion("Revisión del proyecto", "10:00", "11:00"))
# %% [markdown]
# Una dataclass **no valida**: `Reunion(1, None, [])` se crea sin quejarse. Para validar usaremos Pydantic más adelante.
# %% [markdown]
# ## 7 · Errores: fallar pronto y con un mensaje útil
# Las herramientas del curso lanzan `ValueError` cuando la entrada no tiene sentido. Quien llama decide si captura el error o lo deja subir. Un agente recibe ese mensaje y puede corregir el argumento.
# %%
def minutos(hora: str) -> int:
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


def huecos_libres(eventos: list[dict], duracion: int = 30, desde: str = "08:00", hasta: str = "20:00") -> list[dict]:
    """Intervalos libres de al menos `duracion` minutos entre `desde` y `hasta`."""
    if not 5 <= duracion <= 600:
        raise ValueError("La duración debe estar entre 5 y 600 minutos.")
    cursor, fin, huecos = minutos(desde), minutos(hasta), []
    for e in sorted(eventos, key=lambda e: minutos(e["inicio"])):
        if minutos(e["inicio"]) - cursor >= duracion:
            huecos.append({"inicio": f"{cursor // 60:02d}:{cursor % 60:02d}", "fin": e["inicio"]})
        cursor = max(cursor, minutos(e["fin"]))
    if fin - cursor >= duracion:
        huecos.append({"inicio": f"{cursor // 60:02d}:{cursor % 60:02d}", "fin": hasta})
    return huecos



def pedir_hueco(duracion: int) -> str:
    try:
        huecos = huecos_libres(consultar_agenda("2030-05-14"), duracion=duracion)
    except ValueError as exc:
        return f"No se pudo: {exc}"
    return f"{len(huecos)} huecos de al menos {duracion} min"


print(pedir_hueco(60))
print(pedir_hueco(1))
# %% [markdown]
# ## Ejercicio 2 · Gastos por categoría
# Modela un gasto con una `dataclass` (`fecha`, `categoria`, `monto`) y escribe `total_por_categoria(gastos)`, con type hints, que devuelva un diccionario categoría → total redondeado a 2 decimales. Se prueba con `s0/datos/gastos.csv` (mayo de 2030: total 600 Bs, transporte 67 Bs).
# %%
import csv

from copiloto.config import ROOT


# TODO: define la dataclass Gasto con fecha, categoria y monto.
@dataclass
class Gasto:
    pass


# TODO: suma los montos por categoría; anota los tipos de entrada y de salida.
def total_por_categoria(gastos):
    return {}
# %%
from typing import get_type_hints


def cargar_gastos() -> list[Gasto]:
    with (ROOT / "s0/datos/gastos.csv").open(encoding="utf-8") as f:
        return [Gasto(r["fecha"], r["categoria"], float(r["monto"])) for r in csv.DictReader(f)]


revisar("Ejercicio 2 · Gasto es una dataclass con tres campos", lambda: list(Gasto.__dataclass_fields__) == ["fecha", "categoria", "monto"], "Define fecha, categoria y monto en ese orden")
revisar("Ejercicio 2 · total general de 600 Bs", lambda: round(sum(total_por_categoria(cargar_gastos()).values()), 2) == 600, "Suma todos los montos")
revisar("Ejercicio 2 · transporte suma 67 Bs", lambda: total_por_categoria(cargar_gastos())["transporte"] == 67, "Agrupa por g.categoria")
revisar("Ejercicio 2 · la función declara tipos", lambda: get_type_hints(total_por_categoria) == {"gastos": list[Gasto], "return": dict[str, float]}, "Anota gastos: list[Gasto] y el retorno dict[str, float]")
# %% [markdown]
# ## 8 · Asincronía: esperar sin bloquear
# Un agente casi no calcula: **espera**. Espera la respuesta del modelo, de una API de clima, de la base de datos. Con `async def` una función puede ceder el turno en cada `await`; mientras una espera, otra avanza. Con `asyncio.gather` lanzas varias a la vez.
# En un notebook ya hay un bucle de eventos en marcha: escribe `await` directamente (top-level await). `asyncio.run()` dentro de Jupyter falla.
# %%
import asyncio
import time


async def consulta_lenta(nombre: str, segundos: float = 0.3) -> str:
    await asyncio.sleep(segundos)  # imita la espera de una petición de red
    return nombre


t0 = time.perf_counter()
await consulta_lenta("clima")
await consulta_lenta("cambio")
secuencial = time.perf_counter() - t0

t0 = time.perf_counter()
resultados = await asyncio.gather(consulta_lenta("clima"), consulta_lenta("cambio"))
concurrente = time.perf_counter() - t0

print(f"secuencial ≈ {secuencial:.1f} s · concurrente ≈ {concurrente:.1f} s · resultados: {resultados}")
assert concurrente < secuencial
# %% [markdown]
# `gather` devuelve los resultados **en el orden en que pasaste las corrutinas**, no en el orden en que terminaron. Si una falla, la excepción sube a quien hace `await gather(...)`.
# %% [markdown]
# ## 9 · HTTP con httpx
# `httpx` es el cliente HTTP del curso: mismas ideas que `requests`, pero con versión async. Una petición lleva método, URL, cabeceras y, a veces, cuerpo JSON. La respuesta trae un **código de estado** (2xx bien, 4xx error tuyo, 5xx error del servidor) y un cuerpo.
# Para practicar sin internet usamos `httpx.MockTransport`: un «servidor» falso dentro de Python. El código del cliente es idéntico al real.
# %%
import httpx


def servidor_falso(request: httpx.Request) -> httpx.Response:
    ruta = request.url.path
    if ruta == "/clima":
        return httpx.Response(200, json={"ciudad": request.url.params["ciudad"], "max_c": 24})
    if ruta == "/privado":
        if request.headers.get("Authorization") != "Bearer token-de-ejemplo":
            return httpx.Response(401, json={"error": "falta el token"})
        return httpx.Response(200, json={"mensaje": "hola, Alex"})
    if ruta == "/lento":
        raise httpx.ReadTimeout("el servidor tardó demasiado", request=request)
    if ruta == "/caido":
        raise httpx.ConnectError("sin conexión", request=request)
    return httpx.Response(404, json={"error": "no existe"})


transporte = httpx.MockTransport(servidor_falso)
async with httpx.AsyncClient(transport=transporte, base_url="https://api.ejemplo.test", timeout=10) as cliente:
    r = await cliente.get("/clima", params={"ciudad": "Cochabamba"})
    print(r.status_code, r.json())
    sin_token = await cliente.get("/privado")
    con_token = await cliente.get("/privado", headers={"Authorization": "Bearer token-de-ejemplo"})
    print(sin_token.status_code, "→", con_token.status_code, con_token.json())
# %% [markdown]
# Un 404 **no lanza** excepción por sí solo: httpx te devuelve la respuesta. `raise_for_status()` convierte 4xx/5xx en `HTTPStatusError`. Los fallos de red (timeout, conexión rechazada) son otra familia: `TimeoutException` y `TransportError`. Distinguirlos permite dar un mensaje correcto y decidir si reintentar.
# %%
async with httpx.AsyncClient(transport=transporte, base_url="https://api.ejemplo.test", timeout=10) as cliente:
    for ruta in ("/clima?ciudad=Tarata", "/nada", "/lento", "/caido"):
        try:
            r = await cliente.get(ruta)
            r.raise_for_status()
            print(f"{ruta:<24} OK       {r.json()}")
        except httpx.HTTPStatusError as exc:
            print(f"{ruta:<24} HTTP {exc.response.status_code}  la API respondió con error")
        except httpx.TimeoutException:
            print(f"{ruta:<24} TIMEOUT  se puede reintentar una vez")
        except httpx.TransportError:
            print(f"{ruta:<24} RED      no hay conexión con el servidor")
# %% [markdown]
# ### El patrón de las funciones que llaman a una API: timeout, error explícito y fixture offline
# Una función que consulta una API pública sigue casi siempre el mismo patrón: valida sus argumentos, usa un `timeout`, llama a `raise_for_status()` y, con `offline=True`, lee una respuesta real guardada (un **fixture**). Así el código se puede practicar en un aula sin internet. El resultado incluye `simulado` para que nadie confunda un fixture con un dato en vivo.
# %%
# Respuestas guardadas de dos APIs públicas sin clave (Open-Meteo y open.er-api.com).
FIXTURE_CAMBIO = {
    "time_last_update_utc": "Sun, 18 Oct 2026 00:02:31 +0000",
    "rates": {"USD": 1, "BOB": 11.719366, "EUR": 0.889614, "PEN": 3.435525},
}
FIXTURE_CLIMA = {
    "time": ["2026-10-18", "2026-10-19", "2026-10-20"],
    "temperature_2m_max": [29.5, 28.1, 25.4],
    "temperature_2m_min": [8.3, 9.4, 11.7],
    "precipitation_probability_max": [0, 45, 94],
}


async def tipo_cambio(moneda: str = "USD", offline: bool = False) -> dict:
    """Bolivianos por unidad de una moneda (referencia informativa, no tipo oficial)."""
    moneda = moneda.upper()
    if offline:
        datos = FIXTURE_CAMBIO
    else:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://open.er-api.com/v6/latest/USD")
            r.raise_for_status()
            datos = r.json()
    tasas = datos["rates"]
    if moneda not in tasas:
        raise ValueError(f"Moneda {moneda} no disponible.")
    return {
        "moneda": moneda,
        "bob_por_unidad": round(tasas["BOB"] / tasas[moneda], 4),
        "actualizado": datos["time_last_update_utc"],
        "simulado": offline,
    }


async def pronostico_clima(ciudad: str, dias: int = 3, offline: bool = False) -> dict:
    """Pronóstico diario de Cochabamba (en esta versión corta, con coordenadas fijas)."""
    if not 1 <= dias <= 3:
        raise ValueError("Pide entre 1 y 3 días.")
    if offline:
        d = FIXTURE_CLIMA
    else:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": -17.39,
                    "longitude": -66.16,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": "America/La_Paz",
                    "forecast_days": dias,
                },
            )
            r.raise_for_status()
            d = r.json()["daily"]
    return {
        "lugar": f"{ciudad} (Cochabamba)",
        "dias": [
            {
                "fecha": d["time"][i],
                "max_c": d["temperature_2m_max"][i],
                "min_c": d["temperature_2m_min"][i],
                "prob_lluvia": d["precipitation_probability_max"][i],
            }
            for i in range(dias)
        ],
        "simulado": offline,
    }


cambio = await tipo_cambio("USD", offline=True)
print(cambio["moneda"], cambio["bob_por_unidad"], "· simulado:", cambio["simulado"])
try:
    await tipo_cambio("XYZ", offline=True)
except ValueError as exc:
    print("Error explícito:", exc)
# %% [markdown]
# ## Ejercicio 3 · Clima y tipo de cambio en paralelo
# Escribe `async def clima_y_cambio(ciudad)` que obtenga **a la vez** el pronóstico (`pronostico_clima(ciudad, dias=2, offline=True)`) y el tipo de cambio del dólar (`tipo_cambio("USD", offline=True)`) con `asyncio.gather`. Devuelve `{"lugar": ..., "max_hoy": ..., "bob_por_usd": ...}` con el lugar, la temperatura máxima del primer día y los bolivianos por dólar.
# %%
# TODO: usa asyncio.gather con las dos corrutinas y arma el diccionario pedido.
async def clima_y_cambio(ciudad: str) -> dict:
    return {}
# %%
resumen_viaje = await clima_y_cambio("Cochabamba")
print(resumen_viaje)
revisar("Ejercicio 3 · es una función async", lambda: asyncio.iscoroutinefunction(clima_y_cambio), "Usa async def")
revisar("Ejercicio 3 · devuelve el lugar", lambda: "Cochabamba" in resumen_viaje["lugar"], "Copia clima['lugar']")
revisar("Ejercicio 3 · temperatura máxima del primer día", lambda: isinstance(resumen_viaje["max_hoy"], (int, float)), "Usa clima['dias'][0]['max_c']")
revisar("Ejercicio 3 · bolivianos por dólar", lambda: abs(resumen_viaje["bob_por_usd"] - 11.7194) < 0.001, "Usa cambio['bob_por_unidad']")
# %% [markdown]
# ## 10 · Pydantic: validar lo que entra y lo que sale
# `BaseModel` convierte una clase anotada en un **contrato**: al crear el objeto, Pydantic convierte los tipos cuando es razonable (`"45"` → `45`) y rechaza lo que no encaja con un `ValidationError` que dice qué campo falló y por qué. `Field` añade restricciones (`ge`, `le`, `min_length`) y descripciones.
# %%
from pydantic import BaseModel, Field, ValidationError, field_validator


class Tarea(BaseModel):
    titulo: str = Field(min_length=3, max_length=80)
    prioridad: Literal["alta", "media", "baja"] = "media"
    minutos: int = Field(default=30, ge=5, le=480, description="Duración estimada")

    @field_validator("titulo")
    @classmethod
    def sin_espacios_sobrantes(cls, valor: str) -> str:
        return " ".join(valor.split())


tarea = Tarea(titulo="  Leer   capítulo 3 ", minutos="45")
print(repr(tarea))
print(tarea.model_dump())
print(tarea.model_dump_json())
try:
    Tarea(titulo="Ir", prioridad="urgente", minutos=2)
except ValidationError as exc:
    for fallo in exc.errors():
        print(f"{fallo['loc'][0]:<10} → {fallo['msg']}")
# %% [markdown]
# Tres cosas que conviene recordar: (1) los espacios y el `"45"` se corrigieron solos; (2) el error lista **todos** los campos inválidos, no solo el primero; (3) `model_dump()` devuelve un `dict` de Python y `model_dump_json()` un texto JSON listo para enviar.
# %% [markdown]
# ### Validadores: reglas que un tipo no expresa
# `@field_validator` revisa o normaliza **un** campo. `@model_validator(mode="after")` revisa relaciones **entre** campos, por ejemplo «el mínimo no puede superar al máximo». Se lanza `ValueError` y Pydantic lo convierte en `ValidationError`.
# %%
from pydantic import model_validator


class Presupuesto(BaseModel):
    minimo: float = Field(ge=0)
    maximo: float = Field(ge=0)

    @model_validator(mode="after")
    def orden_correcto(self) -> "Presupuesto":
        if self.minimo > self.maximo:
            raise ValueError("el mínimo no puede superar al máximo")
        return self


print(Presupuesto(minimo=100, maximo=250))
try:
    Presupuesto(minimo=300, maximo=250)
except ValidationError as exc:
    print(exc.errors()[0]["msg"])
# %% [markdown]
# ## Ejercicio 4 · El modelo `Evento`
# Define `Evento` con `titulo` (1 a 80 caracteres), `fecha` (`date`), `inicio` y `fin` (`time`) y un `lugar` opcional. Añade un validador que exija **inicio < fin**. Pruébalo con un caso válido y uno inválido.
# %%
from datetime import date, time


# TODO: completa los campos (titulo, fecha, inicio, fin, lugar opcional) y el validador.
class Evento(BaseModel):
    titulo: str
# %%
valido = {"titulo": "Revisión del proyecto", "fecha": "2030-05-14", "inicio": "09:00", "fin": "10:30"}
invalido = {**valido, "inicio": "11:00"}


def rechaza_inicio_tardio() -> bool:
    try:
        Evento(**invalido)
    except ValidationError as exc:
        return "inicio debe ser anterior a fin" in str(exc)
    return False


revisar("Ejercicio 4 · acepta un evento válido", lambda: Evento(**valido).inicio.hour == 9, "Define inicio como time")
revisar("Ejercicio 4 · convierte la fecha", lambda: Evento(**valido).fecha == date(2030, 5, 14), "Define fecha como date")
revisar("Ejercicio 4 · rechaza inicio >= fin con ValidationError", rechaza_inicio_tardio, "Añade un model_validator(mode='after') que lance ValueError")
revisar("Ejercicio 4 · el lugar es opcional", lambda: Evento(**valido).lugar is None, "lugar: str | None = None")
# %% [markdown]
# ## 11 · `model_json_schema()`: lo que ve el modelo de lenguaje
# Este es el **puente a la sesión 1**. Cuando le pides a un agente una salida estructurada, o le registras una tool, Pydantic AI convierte tu modelo (o la firma de tu función) en un **esquema JSON** y se lo envía al LLM. Los nombres de campo, los tipos, las restricciones y las `description` son lo único que el modelo sabe de tu contrato. Un campo mal nombrado o sin descripción es una instrucción deficiente.
# %%
import json

from copiloto.agente import Respuesta

print(json.dumps(Respuesta.model_json_schema(), ensure_ascii=False, indent=2))
# %% [markdown]
# Fíjate en `required`: solo `texto` es obligatorio; `fuentes` y `requiere_revision` tienen valor por defecto. Un campo sin valor por defecto es una exigencia para el modelo.
# %% [markdown]
# ## Ejercicio 5 · Qué campos son obligatorios
# Escribe `campos_requeridos(modelo)` que reciba una clase Pydantic y devuelva la lista de campos obligatorios leyendo `model_json_schema()`. Pruébala con `Respuesta` y con tu `Evento`.
# %%
# TODO: lee la clave "required" del esquema; si no existe, devuelve una lista vacía.
def campos_requeridos(modelo: type[BaseModel]) -> list[str]:
    return []
# %%
print("Respuesta →", campos_requeridos(Respuesta))
print("Evento    →", campos_requeridos(Evento))
revisar("Ejercicio 5 · Respuesta exige solo texto", lambda: campos_requeridos(Respuesta) == ["texto"], "Busca la clave 'required' del esquema")
revisar("Ejercicio 5 · Evento exige titulo, fecha, inicio y fin", lambda: set(campos_requeridos(Evento)) == {"titulo", "fecha", "inicio", "fin"}, "Completa antes el ejercicio 4")
revisar("Ejercicio 5 · un modelo sin obligatorios devuelve lista vacía", lambda: campos_requeridos(type("Vacio", (BaseModel,), {})) == [], "Usa .get('required', [])")
# %% [markdown]
# ## 12 · Configuración y secretos
# `Settings` (en `copiloto/config.py`) usa `pydantic-settings`: lee variables de entorno y el archivo `.env`, valida tipos y restricciones y guarda las claves como `SecretStr`. Un `SecretStr` se imprime como `**********`; para usar el valor real hay que pedirlo con `.get_secret_value()`, en el único lugar que lo necesita.
# **El archivo `.env` nunca se sube a Git** (`.gitignore` lo excluye). Lo que se versiona es `.env.example`, sin valores reales.
# %%
from copiloto.config import Settings

campos = settings.model_dump(include={"mode", "ollama_model", "gemini_model", "request_limit"})
print(campos)
ejemplo = Settings(_env_file=None, openrouter_api_key="clave-de-ejemplo")
print("Clave en print:", ejemplo.openrouter_api_key)
print("Clave en repr :", repr(ejemplo.openrouter_api_key))
print("¿Mi .env tiene clave de Gemini?", bool(settings.gemini_api_key.get_secret_value()))
try:
    Settings(_env_file=None, request_limit=99)
except ValidationError as exc:
    print("Configuración inválida:", exc.errors()[0]["msg"])
# %% [markdown]
# ## Ejercicio 6 · Un secreto que no se imprime
# Crea `ajustes_demo` con `Settings(_env_file=None, gemini_api_key=TOKEN_FALSO, request_limit=5)`, ignorando tu `.env` real. Luego arma `linea_log`, una línea de log que mencione el token **sin revelarlo**. Comprueba que `.get_secret_value()` sí devuelve el valor original.
# %%
TOKEN_FALSO = "clave-de-prueba-123"

# TODO: crea los ajustes con el token falso y arma la línea de log sin revelar el secreto.
ajustes_demo = None
linea_log = ""
print(linea_log)
# %%
revisar("Ejercicio 6 · ajustes creados con límite 5", lambda: ajustes_demo.request_limit == 5, "Pasa request_limit=5")
revisar("Ejercicio 6 · el log no contiene el token", lambda: TOKEN_FALSO not in linea_log and "**" in linea_log, "Interpola el SecretStr, no get_secret_value()")
revisar("Ejercicio 6 · repr de la configuración no filtra el token", lambda: TOKEN_FALSO not in repr(ajustes_demo), "SecretStr oculta el valor en repr")
revisar("Ejercicio 6 · el valor real sigue disponible", lambda: ajustes_demo.gemini_api_key.get_secret_value() == TOKEN_FALSO, "Usa get_secret_value() solo donde se necesita")
# %% [markdown]
# ## Autoevaluación
# Responde primero sin mirar; abre la respuesta después.
# 0a. ¿Qué cambia en las respuestas de un modelo al subir la temperatura y por qué un agente usa `temperature=0`?
# 0b. ¿Qué distingue a un sistema agéntico de uno generativo?
# 1. ¿Qué comando recrea exactamente el entorno del curso a partir de `uv.lock`?
# 2. ¿Qué diferencia hay entre un `404` y un timeout al llamar a una API con httpx?
# 3. ¿Por qué `await a(); await b()` tarda más que `await asyncio.gather(a(), b())`?
# 4. ¿Qué devuelve Pydantic cuando los datos no cumplen el modelo y qué información trae?
# 5. ¿Por qué se usa `SecretStr` para una clave y dónde se guarda su valor real?
# <details><summary>Respuestas</summary>
#
# 0a. Con temperatura alta se muestrean tokens menos probables y las respuestas varían; un agente que ejecuta acciones necesita repetibilidad.
# 0b. Que usa herramientas y decide sus pasos en un bucle hacia un objetivo; el generativo solo produce contenido.
# 1. `uv sync`: instala las versiones fijadas en `uv.lock` sin recalcularlas.
# 2. El 404 es una respuesta del servidor (hay que llamar a `raise_for_status()` para convertirla en excepción); el timeout es un fallo de red sin respuesta (`TimeoutException`).
# 3. En la forma secuencial cada espera empieza cuando termina la anterior; con `gather` las esperas se solapan y el tiempo total es el de la más lenta.
# 4. Un `ValidationError` con la lista de errores: campo (`loc`), mensaje (`msg`), tipo y valor recibido.
# 5. Para que no aparezca en `print`, `repr` ni logs. El valor real vive en `.env` o en las variables de entorno, nunca en Git.
# </details>
# %% [markdown]
# ## Checklist: estoy listo para la sesión 1
# - [ ] Distingo IA predictiva, generativa y agéntica, y sé qué son un token y la temperatura.
# - [ ] `uv run copiloto-doctor` termina sin errores.
# - [ ] Este notebook corre completo con el kernel del `.venv` y mis seis ejercicios muestran ✅.
# - [ ] Sé crear un modelo Pydantic con `Field`, interpretar un `ValidationError` y leer `model_json_schema()`.
# - [ ] Sé escribir `await` en una celda y usar `asyncio.gather`.
# - [ ] Mi `.env` existe, no está en Git y no pegué su contenido en ningún chat.
# - [ ] Tengo anotado un problema concreto para consultarlo en los 10 minutos de repaso de la sesión 1.
# %% [markdown]
# ## Cierre
# Ya sabes qué tipo de IA vamos a construir (agéntica) y con qué piezas de Python. Con ellas puedes leer el código de Mi copiloto: funciones con tipos, llamadas async con fixtures, contratos Pydantic y configuración con secretos.
# **Adelanto de la sesión 1:** pasaremos del chat al agente. Verás cómo `Respuesta.model_json_schema()` se convierte en la **salida estructurada** que el modelo debe respetar y ejecutarás tu primer agente de Pydantic AI.
