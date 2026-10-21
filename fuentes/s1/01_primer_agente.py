# Fuente de notebook Jupyter con top-level await; regenerar con fuentes/generar_notebooks.py.
# ruff: noqa: F704
# %% [markdown]
# # 1 · De los chatbots a los agentes de IA
# **Pregunta:** ¿qué tiene un agente que no tiene un chatbot, y qué parte es del modelo y qué parte es de nuestro código?
# **Producto:** el bucle de un agente escrito desde cero (con un «modelo» de juguete y con un LLM real) y el primer Mi copiloto en Pydantic AI, con instrucciones y salida estructurada.
# **Al terminar:** podrás explicar el ciclo pedir → ejecutar → observar, escribir el despachador de tools de un agente, definir un `output_type` propio, comparar respuesta libre y tipada midiendo el uso, y cambiar de modelo sin tocar el código del agente.
# **Formato:** 60 minutos, solo o en parejas. Todo se ejecuta sin red ni LLM (`COURSE_OFFLINE=1`, el valor por defecto). Las celdas con IA real van protegidas con `if not OFFLINE:`.
# %% [markdown]
# ## Preparación reproducible
# Las dependencias se instalan **antes** de abrir el notebook (`uv sync`, ver el README del repositorio). Si algo falla, `uv run copiloto-doctor` dice qué parte del entorno no responde.
# Por defecto el notebook usa el **modelo simulado**: elige tools por palabras clave y rellena cualquier `output_type`. No es inteligencia artificial y **no mide calidad**; sirve para ver el recorrido completo sin red ni cuota. Para IA real: configura `.env` (ruta y clave), ejecuta `uv run copiloto-doctor --live`, pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel (botón **Restart** de la barra del notebook en VS Code).
# %%
from copiloto.practica import preparar, revisar, ver_mensajes

settings, OFFLINE = preparar()
# %% [markdown]
# ## 1 · ¿Con qué modelo trabajo hoy?
# El mismo agente corre con cuatro «motores»; solo cambia una línea de `.env` (repasa `s0/02_repaso.ipynb` si «token» o «temperatura» no te suenan):
#
# | Ruta | `.env` | Datos |
# |---|---|---|
# | Gemini gratis | `MODE=gemini` + `GEMINI_API_KEY` (ver [docs/gemini.md](../docs/gemini.md)) | Viajan a Google; solo datos ficticios |
# | OpenRouter gratis | `MODE=openrouter` + `OPENROUTER_API_KEY` + un ID `:free` (ver [docs/openrouter.md](../docs/openrouter.md)) | Viajan al proveedor del modelo |
# | Ollama local | `MODE=local` + `OLLAMA_MODEL` (ver [docs/ollama.md](../docs/ollama.md)) | No salen de tu equipo |
# | Simulado | `COURSE_OFFLINE=1` (por defecto) | Sin IA real |
#
# La celda muestra qué ruta está activa. Si dice «simulado» y quieres IA real, pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel.
# %%
from copiloto.config import describir_modelo

print("Modelo activo:", describir_modelo(settings, OFFLINE))
if not OFFLINE and settings.mode == "gemini":
    print("Gemini (capa gratuita): si aparece 429, espera un minuto o cambia GEMINI_MODEL.")
# %% [markdown]
# ## 2 · Un agente desde cero: ReAct en unas 40 líneas
# **ReAct** (Yao et al., 2023) intercala *razonar*, *actuar* y *observar*. Antes de usar un framework escribimos el bucle en Python puro, como en la práctica de DeepLearning.AI. Necesitamos cuatro piezas: una tool, un «modelo», un despachador y el bucle.
# Primero la **tool** (una función de `herramientas/`, sin cambios) y un **«modelo» de juguete**: una función que devuelve JSON. Pide la tool la primera vez y, cuando ve el resultado, responde. No entiende nada: solo nos deja ver el bucle sin red.
# %%
import json
import re

from copiloto.herramientas import calcular_presupuesto

PEDIDO = "Calcula el presupuesto de 3 horas de taller a 40 Bs por hora."
TOOLS = {"calcular_presupuesto": calcular_presupuesto}


def modelo_juguete(mensajes: list[dict]) -> str:
    """Un «modelo» de mentira: devuelve JSON. No es IA."""
    ultimo = mensajes[-1]
    if ultimo["role"] == "tool":
        datos = json.loads(ultimo["content"])
        return json.dumps({"respuesta": f"El presupuesto es {datos['total']} {datos['moneda']}."})
    horas, tarifa = re.findall(r"\d+(?:\.\d+)?", ultimo["content"])[:2]
    return json.dumps(
        {
            "pensamiento": "Debo multiplicar horas por tarifa",
            "tool": "calcular_presupuesto",
            "args": {"horas": float(horas), "tarifa": float(tarifa)},
        }
    )


print(modelo_juguete([{"role": "user", "content": PEDIDO}]))
# %% [markdown]
# Ahora el **despachador** (ejecuta la tool que pidió el modelo y devuelve su resultado como texto) y el **bucle**: pedir al modelo, ejecutar, devolver el resultado y repetir hasta que responda. `max_pasos` es el control más barato contra un bucle infinito.
# %%
def ejecutar_tool(pedido: dict) -> str:
    funcion = TOOLS[pedido["tool"]]
    return json.dumps(funcion(**pedido["args"]), ensure_ascii=False)


def agente(pedido: str, modelo=modelo_juguete, despachar=ejecutar_tool, max_pasos: int = 5) -> str:
    mensajes = [{"role": "user", "content": pedido}]
    for _ in range(max_pasos):
        salida = json.loads(modelo(mensajes))
        if "respuesta" in salida:
            return salida["respuesta"]
        print(f"💭 {salida.get('pensamiento', '')}")
        print(f"🤖 pide tool {salida['tool']}({salida['args']})")
        observacion = despachar(salida)
        print(f"🔧 resultado {observacion}")
        mensajes.append({"role": "assistant", "content": json.dumps(salida)})
        mensajes.append({"role": "tool", "content": observacion})
    raise RuntimeError(f"Sin respuesta tras {max_pasos} pasos")


print("✅", agente(PEDIDO))
# %% [markdown]
# Eso es un agente: un **modelo que pide**, un **programa que valida y ejecuta**, y un **ciclo con límite**. Todo lo demás (esquemas, reintentos, historial, aprobación humana) son mejoras a este mismo esqueleto.
# %% [markdown]
# ### 2.1 · Con un LLM real: `/chat/completions`
# Ollama, Gemini y OpenRouter ofrecen una API compatible con OpenAI. El protocolo de tools es el mismo para casi todos los proveedores: enviamos `tools` (un JSON Schema por función), el modelo responde con `tool_calls` y nosotros contestamos con mensajes de rol `tool`. Fíjate en que **el esquema se escribe a mano**: es lo primero que un framework nos ahorra.
# Esta celda solo corre con IA real (`COURSE_OFFLINE=0`) y usa la ruta de tu `.env` (`ruta_openai` devuelve URL, clave y modelo según `MODE`). Si el modelo no responde, imprime una pista y el notebook sigue. Una versión con una sola interfaz de modelo está en `s1/bucle_sin_framework.py`.
# %%
if not OFFLINE:
    import httpx

    from copiloto.config import ruta_openai

    HERRAMIENTAS = [
        {
            "type": "function",
            "function": {
                "name": "calcular_presupuesto",
                "description": calcular_presupuesto.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {"horas": {"type": "number"}, "tarifa": {"type": "number"}},
                    "required": ["horas", "tarifa"],
                },
            },
        }
    ]

    def agente_llm(pedido: str, max_pasos: int = 5) -> str:
        base, clave, modelo = ruta_openai(settings)
        mensajes = [{"role": "user", "content": pedido}]
        for _ in range(max_pasos):
            cuerpo = {
                "model": modelo,
                "messages": mensajes,
                "tools": HERRAMIENTAS,
                "temperature": 0,
            }
            r = httpx.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {clave}"},
                json=cuerpo,
                timeout=120,
            )
            r.raise_for_status()
            mensaje = r.json()["choices"][0]["message"]
            llamadas = mensaje.get("tool_calls") or []
            if not llamadas:
                return mensaje["content"]
            mensajes.append(
                {"role": "assistant", "content": mensaje.get("content") or "", "tool_calls": llamadas}
            )
            for llamada in llamadas:
                nombre, args = llamada["function"]["name"], llamada["function"]["arguments"]
                args = json.loads(args) if isinstance(args, str) else args
                print(f"🤖 pide tool {nombre}({args})")
                observacion = ejecutar_tool({"tool": nombre, "args": args})
                print(f"🔧 resultado {observacion}")
                mensajes.append(
                    {"role": "tool", "tool_call_id": llamada["id"], "content": observacion}
                )
        raise RuntimeError(f"Sin respuesta tras {max_pasos} pasos")

    try:
        print("✅", agente_llm(PEDIDO))
    except (httpx.HTTPError, ValueError) as exc:
        print(f"El modelo no respondió ({type(exc).__name__}: {str(exc)[:120]}). Prueba: uv run copiloto-doctor --live")
# %% [markdown]
# ### 2.2 · Lo mismo con Pydantic AI
# Con el framework, el esquema sale de la **firma y el docstring** de la función, los argumentos se validan, el bucle y sus límites ya existen y los mensajes quedan tipados. `ver_mensajes` muestra el mismo recorrido que imprimimos a mano.
# %%
from pydantic_ai import Agent
from pydantic_ai.tools import Tool

from copiloto.config import crear_modelo

agente_pai = Agent(
    crear_modelo(settings, OFFLINE),
    instructions="Responde en español y breve. Usa las herramientas para calcular.",
    tools=[calcular_presupuesto],
)
resultado = await agente_pai.run(PEDIDO)
ver_mensajes(resultado)
print(resultado.output)
# %% [markdown]
# Compara con el esquema que escribimos a mano en 2.1: Pydantic AI lo **derivó** de `calcular_presupuesto(horas: float, tarifa: float)`.
# %%
print(Tool(calcular_presupuesto).tool_def.parameters_json_schema)
# %% [markdown]
# ## 3 · El primer agente de Mi copiloto
# `crear_agente_basico` (en `copiloto/agente.py`) reúne tres piezas: un **modelo** (`crear_modelo`), unas **instrucciones** (`INSTRUCCIONES`) y un **contrato de salida** (`Respuesta`). Todavía no tiene tools, memoria ni capacidades: esas llegan en las sesiones 2 y 3.
# Lee las instrucciones como un contrato de comportamiento: dicen qué hacer, qué no inventar, cómo tratar los documentos y cuándo pedir aprobación.
# %%
from copiloto.agente import INSTRUCCIONES, crear_agente_basico
from copiloto.agente import Respuesta

print(INSTRUCCIONES)
print(Respuesta.model_json_schema()["properties"].keys())
# %% [markdown]
# Ejecutamos una petición con objetivo, restricciones y un criterio de éxito. `resultado.output` es un objeto `Respuesta` ya validado; `resultado.usage` cuenta requests y tokens; `ver_mensajes` muestra el recorrido.
# %%
basico = crear_agente_basico(settings, offline=OFFLINE)
PETICION = (
    "Soy Alex. Hoy tengo una cita a las 09:00 y quiero leer 60 minutos y caminar 30. "
    "Propón tres bloques sin solapar la cita e indica qué dato falta para planificar bien."
)
r_basico = await basico.run(PETICION)
print(r_basico.output.model_dump())
print(r_basico.usage)
ver_mensajes(r_basico)
# %% [markdown]
# Los **mensajes** son la memoria de corto plazo de una ejecución: `all_messages()` devuelve la lista completa (petición, respuesta del modelo, resultados de tools). Inspecciona los tipos; no imprimas historiales con datos reales.
# %%
print([type(m).__name__ for m in r_basico.all_messages()])
# %% [markdown]
# ## 4 · Respuesta libre y respuesta tipada
# Sin `output_type` el agente devuelve **texto**; con `output_type=Respuesta` devuelve un objeto validado. Lo tipado cuesta algo más (el esquema viaja al modelo y la respuesta lleva campos), pero tu interfaz recibe una estructura estable en lugar de un párrafo que hay que interpretar.
# %%
libre = Agent(crear_modelo(settings, OFFLINE), instructions=INSTRUCCIONES)
r_libre = await libre.run(PETICION)
print("libre  :", type(r_libre.output).__name__, "·", r_libre.usage)
print("tipado :", type(r_basico.output).__name__, "·", r_basico.usage)
# %% [markdown]
# ## 5 · Modos de salida: Tool, Native y Prompted
# Pydantic AI puede pedir la salida estructurada de tres maneras: como una **tool de salida** (por defecto), con el **JSON nativo** del proveedor (`NativeOutput`) o con el **esquema dentro del prompt** (`PromptedOutput`). `esquema_salida` (en `copiloto/agente.py`) elige según el proveedor:
# - Ollama **sin tools** → `NativeOutput` (JSON forzado por gramática).
# - Ollama **con tools** → `PromptedOutput`: pedir `response_format=json_object` impediría emitir llamadas a tools.
# - Otros proveedores → la clase directa (modo Tool).
# %%
from copiloto.agente import esquema_salida

local = settings.model_copy(update={"mode": "local", "model": ""})
print("este notebook      :", esquema_salida(settings, OFFLINE))
print("Ollama sin tools   :", type(esquema_salida(local)).__name__)
print("Ollama con tools   :", type(esquema_salida(local, con_tools=True)).__name__)
# %% [markdown]
# ## 6 · Un esquema válido no garantiza un dato verdadero
# `Respuesta` exige que `texto` no esté vacío, que `fuentes` sea una lista y que `requiere_revision` sea booleano. Nada más. Un modelo puede cumplir el contrato y **mentir**: la validación revisa la forma; la verdad se comprueba con tools, fuentes y evaluaciones (sesiones 2 y 6).
# %%
inventada = Respuesta(
    texto="Tu reunión con Ana es mañana a las 15:00 en la sala azul.",
    fuentes=["agenda:inventada"],
)
print("¿válida?", Respuesta.model_validate(inventada.model_dump()) == inventada)
print("¿verdadera? Este agente no tiene ninguna tool que lo confirme.")
# %% [markdown]
# ## 7 · Leer los errores: ¿falló el modelo o falló el programa?
# - **Falla el programa** (entorno, red, clave): `ConnectError`, `UserError`, `ModuleNotFoundError`. Se arregla fuera del modelo.
# - **Falla el modelo** (salida inválida): Pydantic AI devuelve el error al modelo para que reintente; si agota los reintentos lanza `UnexpectedModelBehavior`.
# - **Salta un límite** que tú pusiste: `UsageLimitExceeded`. Es el control funcionando, no un fallo.
# Aquí provocamos los dos últimos sin red, con un modelo que siempre responde mal.
# %%
from pydantic_ai import UnexpectedModelBehavior, UsageLimitExceeded, UsageLimits
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel


def modelo_que_falla(mensajes, info):
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"texto": ""})])


agente_fallido = Agent(FunctionModel(modelo_que_falla), output_type=Respuesta, retries=1)
try:
    await agente_fallido.run("Hola")
except UnexpectedModelBehavior as exc:
    print("El modelo falló →", type(exc).__name__, "·", exc)
try:
    await basico.run("Hola", usage_limits=UsageLimits(request_limit=0))
except UsageLimitExceeded as exc:
    print("Un límite saltó →", type(exc).__name__)
# %% [markdown]
# ## 8 · El mismo pedido con otro modelo (solo IA real)
# El agente no cambia: cambia la variable. `MODE=local` usa Ollama con `OLLAMA_MODEL`; `MODE=gemini` usa Gemini con `GEMINI_MODEL`; `MODE=openrouter`, el modelo `:free` de `OPENROUTER_MODEL`; `MODEL=proveedor:modelo` usa cualquier modelo de Pydantic AI (ver `.env.example`). Esta celda ejecuta el pedido con el modelo configurado y muestra requests y tokens; en el ejercicio 5 la generalizas para comparar dos modelos.
# %%
if not OFFLINE:
    try:
        r_real = await crear_agente_basico(settings).run(PETICION)
        print(r_real.output.model_dump())
        print(r_real.usage)
    except Exception as exc:
        print(f"Falló el programa, no el esquema: {type(exc).__name__}: {str(exc)[:160]}")
# %% [markdown]
# ## Ejercicio 1 · Instrucciones para otra persona
# Mi copiloto trabaja para Alex. Escribe instrucciones para **otro rol** (una coordinadora de un colectivo, un docente, una voluntaria…) con tres reglas: responder en español, **no inventar** datos y decir qué falta cuando no hay evidencia. Se prueban con el mismo contrato `Respuesta`.
# %%
# TODO: escribe tus instrucciones (rol, español, no inventar, qué falta) entre las comillas.
mis_instrucciones = ""
agente_propio = Agent(
    crear_modelo(settings, OFFLINE),
    instructions=mis_instrucciones,
    output_type=esquema_salida(settings, OFFLINE),
)
r1 = await agente_propio.run("¿Cuántas personas vienen al taller del sábado?")
print(r1.output.model_dump())
# %%
revisar(
    "Ejercicio 1 · pide español y no inventar",
    lambda: "español" in mis_instrucciones.lower() and "no invent" in mis_instrucciones.lower(),
    "Incluye «español» y «No inventes datos» en tus instrucciones",
)
revisar(
    "Ejercicio 1 · el contrato se cumple",
    lambda: isinstance(r1.output, Respuesta) and bool(mis_instrucciones.strip()),
    "La salida debe ser una Respuesta y las instrucciones no pueden estar vacías",
)
# %% [markdown]
# ## Ejercicio 2 · Tu propio `output_type`: `PlanDia`
# Define un contrato para un plan del día: una **lista de bloques** (hora y actividad) y un `dato_faltante` opcional (`str | None`) para cuando falta información. Crea un agente con ese `output_type` y comprueba con `isinstance` que la salida es un `PlanDia`. Mira `copiloto/agente.py`: `Paso` y `Plan` son parientes de lo que vas a escribir.
# %%
from pydantic import BaseModel, Field


class Bloque(BaseModel):
    hora: str = Field(description="HH:MM")
    actividad: str


# TODO: añade los campos `bloques` (lista de Bloque) y `dato_faltante` (str | None, por defecto None).
class PlanDia(BaseModel):
    pass


agente_plan = Agent(
    crear_modelo(settings, OFFLINE),
    instructions=INSTRUCCIONES,
    output_type=esquema_salida(settings, OFFLINE, tipo=PlanDia),
)
r2 = await agente_plan.run(PETICION)
print(r2.output)
# %%
revisar(
    "Ejercicio 2 · PlanDia tiene bloques y dato_faltante",
    lambda: {"bloques", "dato_faltante"} <= set(PlanDia.model_fields),
    "Añade los campos bloques y dato_faltante",
)
revisar(
    "Ejercicio 2 · acepta un plan válido",
    lambda: PlanDia(
        bloques=[Bloque(hora="09:00", actividad="Cita")], dato_faltante="duración de la cita"
    ).bloques[0].hora
    == "09:00",
    "bloques es una lista de Bloque y dato_faltante es opcional",
)
revisar("Ejercicio 2 · el agente devuelve un PlanDia", lambda: isinstance(r2.output, PlanDia), "")
# %% [markdown]
# ## Ejercicio 3 · Un despachador que sobrevive a los errores
# Un modelo real a veces **pide una tool que no existe** o con argumentos mal formados. Con `ejecutar_tool`, el programa se cae con un `KeyError`. Escribe `despachar_seguro`: debe devolver siempre un texto JSON; si la tool no existe o los argumentos fallan, devuelve `{"error": "..."}` como observación para que el modelo pueda corregirse. Es la idea de `ModelRetry` en Pydantic AI.
# %%
def modelo_travieso(mensajes: list[dict]) -> str:
    """Primero pide una tool inventada; si ve un error, corrige y pide la correcta."""
    ultimo = mensajes[-1]
    if ultimo["role"] == "user":
        return json.dumps({"pensamiento": "Pruebo una tool", "tool": "presupuestar", "args": {}})
    if "error" in ultimo["content"]:
        return modelo_juguete(mensajes[:1])
    return modelo_juguete(mensajes)


# TODO: captura la tool inexistente y los argumentos inválidos y devuelve {"error": "..."} en JSON.
def despachar_seguro(pedido: dict) -> str:
    return ejecutar_tool(pedido)


try:
    respuesta_3 = agente(PEDIDO, modelo_travieso, despachar=despachar_seguro)
except Exception as exc:  # mientras el ejercicio esté incompleto
    respuesta_3 = f"{type(exc).__name__}: {exc}"
print(respuesta_3)
# %%
revisar(
    "Ejercicio 3 · la tool inexistente devuelve un error en JSON",
    lambda: "error" in json.loads(despachar_seguro({"tool": "presupuestar", "args": {}})),
    "Captura KeyError y devuelve json.dumps({'error': ...})",
)
revisar(
    "Ejercicio 3 · argumentos inválidos también",
    lambda: "error" in json.loads(despachar_seguro({"tool": "calcular_presupuesto", "args": {"x": 1}})),
    "Captura TypeError (argumentos que la función no acepta)",
)
revisar(
    "Ejercicio 3 · el agente se recupera y responde 120",
    lambda: "120" in respuesta_3,
    "Con el despachador seguro el modelo ve el error, corrige y responde",
)
# %% [markdown]
# ## Ejercicio 4 · Libre contra tipada: mide el uso
# Escribe `medir(agente, pedido)`: ejecuta el agente y devuelve un diccionario con `requests`, `entrada`, `salida` (tokens) y `segundos`. Úsala con el agente libre y el tipado del apartado 4. Con el modelo simulado los tokens son una estimación; con IA real son los que reporta el proveedor.
# %%


# TODO: ejecuta el agente y devuelve {"requests", "entrada", "salida", "segundos"}.
async def medir(agente, pedido: str) -> dict:
    return {}


m_libre = await medir(libre, PETICION)
m_tipado = await medir(basico, PETICION)
print("libre :", m_libre)
print("tipado:", m_tipado)
# %%
CLAVES = {"requests", "entrada", "salida", "segundos"}
revisar(
    "Ejercicio 4 · medir devuelve las cuatro métricas",
    lambda: CLAVES <= set(m_libre) and CLAVES <= set(m_tipado),
    "Devuelve requests, entrada, salida y segundos",
)
revisar(
    "Ejercicio 4 · al menos una request y tokens contados",
    lambda: m_tipado["requests"] >= 1 and m_tipado["entrada"] > 0 and m_tipado["salida"] > 0,
    "Lee r.usage.requests, r.usage.input_tokens y r.usage.output_tokens",
)
# %% [markdown]
# ## Ejercicio 5 (reto, IA real) · Mismo pedido, dos modelos
# Generaliza `medir`: `comparar(pedido, variantes)` crea un agente básico por cada variante de configuración (un diccionario para `settings.model_copy(update=...)`), lo ejecuta y devuelve una fila por modelo con `modelo` (`describir_modelo`), `requests`, `entrada`, `salida` y `segundos`. La celda elige las variantes según tu ruta: con `MODE=gemini` compara `gemini-3.5-flash-lite` y `gemini-3.8-flash`; con `MODE=openrouter`, tu modelo `:free` frente a Ollama; con Ollama, `qwen3:4b-instruct` y `qwen3.5:4b`. Para mezclar local y nube usa, por ejemplo, `{"mode": "local"}` y `{"mode": "gemini"}`.
# En offline las dos filas usan el modelo simulado: la función se comprueba igual, pero la comparación solo tiene sentido con IA real. Si un modelo falla (no descargado, lento, sin clave), su fila lleva `error` en vez de métricas: atrapa la excepción por variante. `qwen3.5:4b` piensa antes de responder: la primera llamada puede tardar más de un minuto; caliéntalo antes con `ollama run qwen3.5:4b hola`.
# %%

if settings.mode == "gemini":
    VARIANTES = [{"gemini_model": "gemini-3.5-flash-lite"}, {"gemini_model": "gemini-3.8-flash"}]
elif settings.mode == "openrouter":
    VARIANTES = [{}, {"mode": "local"}]  # tu modelo :free frente a Ollama local
else:
    VARIANTES = [{"ollama_model": "qwen3:4b-instruct"}, {"ollama_model": "qwen3.5:4b"}]


# TODO: para cada variante crea settings.model_copy(update=cambios), un agente básico y mide.
async def comparar(pedido: str, variantes: list[dict]) -> list[dict]:
    return []


try:
    filas = await comparar(PETICION, VARIANTES)
except Exception as exc:  # modelo no descargado, sin clave o sin red: falla el programa
    filas = []
    print(f"No se pudo comparar: {type(exc).__name__}: {str(exc)[:160]}")
for fila in filas:
    print(fila)
# %%
revisar(
    "Ejercicio 5 · una fila por modelo con las métricas",
    lambda: len(filas) == 2
    and all("modelo" in f and (CLAVES <= set(f) or "error" in f) for f in filas),
    "Una fila por variante con modelo y métricas (o «error» si ese modelo falló)",
)
# %% [markdown]
# ## Evidencia y cierre
# Guarda en tu entrega: tu `PlanDia`, el despachador seguro, la tabla de `comparar` y una frase sobre lo que **no** pudo comprobar la validación del esquema. Entrega el notebook con tus cambios y, si puedes, con las salidas de la ejecución con IA real.
# **¿Qué puede hacer ahora Mi copiloto que antes no podía?** Responde en español con instrucciones propias, devuelve objetos validados (`Respuesta`, `PlanDia`) y puedes medir lo que cuesta cada ejecución. Todavía **no consulta nada**: no ve la agenda, el correo ni los gastos de Alex. Si te pregunta «¿qué tengo mañana?», solo puede reconocer que le falta el dato.
# **Sesión 2:** le damos herramientas (agenda, correo, tareas, finanzas) para que consulte y actúe, todo desde la terminal. La API y el bot de Telegram llegan en la sesión 6, con el despliegue.
# **Preguntas para pensar:** ¿qué parte de tu `agente()` de Python puro hace hoy Pydantic AI por ti? ¿Qué control añadirías antes de dejar que el agente ejecute una acción que escribe?
