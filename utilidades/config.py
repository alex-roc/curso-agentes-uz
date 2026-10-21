"""Una configuración para notebooks y scripts: las rutas de modelo del curso.

Cambiar de modelo es cambiar una variable (`MODE` en `.env`); el código del agente no cambia."""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

ROOT = Path(__file__).resolve().parents[1]


class _DotEnvSinVacios(DotEnvSettingsSource):
    """`.env` sin las líneas vacías (`GEMINI_API_KEY=`): una plantilla sin rellenar no debe
    tapar una variable que sí exista en el entorno."""

    def __call__(self) -> dict:
        return {k: v for k, v in super().__call__().items() if v not in ("", None)}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    # local = Ollama; gemini = API de Google (capa gratuita); openrouter = modelos :free;
    # offline = modelo simulado, sin IA real.
    mode: Literal["local", "gemini", "openrouter", "offline"] = "local"
    # Solo para notebooks: 1 = modelo simulado aunque MODE sea otro; 0 = usa la ruta de MODE.
    course_offline: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e2b"
    # Clave de Google AI Studio (gratis, sin tarjeta). Guía: docs/gemini.md
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-3.5-flash-lite"
    openrouter_api_key: SecretStr = SecretStr("")
    openrouter_model: str = ""
    request_limit: int = Field(default=8, ge=1, le=30)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """`.env` gana sobre las variables de entorno: lo que configuraste con
        `python -m utilidades.configurar` es lo que se usa, aunque tu terminal exporte otra clave."""
        return (
            init_settings,
            _DotEnvSinVacios(
                settings_cls,
                env_file=dotenv_settings.env_file,
                env_file_encoding=dotenv_settings.env_file_encoding,
            ),
            env_settings,
            file_secret_settings,
        )

    @property
    def offline(self) -> bool:
        return self.mode == "offline"


def describir_ruta(settings: Settings, offline: bool = False) -> str:
    """Texto corto de la ruta activa, p. ej. `google:gemini-3.5-flash-lite`."""
    if offline or settings.offline:
        return "simulado (sin LLM)"
    if settings.mode == "local":
        return f"ollama:{settings.ollama_model}"
    if settings.mode == "gemini":
        return f"google:{settings.gemini_model}"
    return f"openrouter:{settings.openrouter_model}"


def validar_ruta(settings: Settings) -> None:
    """Falla con un mensaje claro si a la ruta elegida le falta clave o modelo."""
    if settings.mode == "gemini" and not settings.gemini_api_key.get_secret_value():
        raise ValueError(
            "Falta GEMINI_API_KEY. Créala gratis en https://aistudio.google.com/apikey"
        )
    if settings.mode == "openrouter":
        if not settings.openrouter_model.endswith(":free"):
            raise ValueError(
                "MODE=openrouter requiere un OPENROUTER_MODEL concreto que termine en :free "
                "(mira docs/openrouter.md)."
            )
        if not settings.openrouter_api_key.get_secret_value():
            raise ValueError(
                "Falta OPENROUTER_API_KEY. Créala gratis en https://openrouter.ai/keys"
            )


def crear_modelo(settings: Settings, offline: bool = False):
    """Devuelve el modelo de Pydantic AI de la ruta elegida: es lo que recibe `Agent(modelo)`.

    - `MODE=local`: Ollama en tu equipo, vía la API compatible con OpenAI
      (`OpenAIChatModel` + `OllamaProvider`).
    - `MODE=gemini`: la API de Google (`GoogleModel` + `GoogleProvider`).
    - `MODE=openrouter`: un modelo `:free` (`OpenRouterModel` + `OpenRouterProvider`).
    - Modo simulado: un `FunctionModel` sin IA (ver `simulado.py`).

    No cambia en silencio a proveedores de pago ni a modelos simulados: si a la ruta le
    falta algo, `validar_ruta` lanza un error con el arreglo.

    Gotcha de Ollama con tools: el modelo local no admite a la vez herramientas y salida JSON
    forzada por gramática. Si el agente tiene tools y un `output_type` estructurado, ese tipo
    se envuelve a mano en `PromptedOutput(tipo)` (sin tools basta `NativeOutput(tipo)`). Eso lo
    decide el código del agente, no esta función, para que se vea en el notebook.

    Cuotas gratuitas: Gemini y OpenRouter responden 429 cuando se pasa el límite **por minuto**
    (Gemini gratis: unas 15 peticiones por minuto y modelo; un pedido con tools gasta 2-4).
    Estas rutas reintentan solas, esperando lo que indica el servidor, durante un minuto como
    mucho. Si la cuota agotada es la **del día**, el error 429 sigue apareciendo: cambia de
    modelo, espera o usa el modo simulado.
    """
    if offline or settings.offline:
        from .simulado import modelo_simulado

        return modelo_simulado()
    validar_ruta(settings)
    if settings.mode == "local":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.profiles import merge_profile
        from pydantic_ai.profiles.openai import OpenAIModelProfile
        from pydantic_ai.providers.ollama import OllamaProvider

        nombre = settings.ollama_model
        return OpenAIChatModel(
            nombre,
            provider=OllamaProvider(base_url=settings.ollama_base_url.rstrip("/") + "/v1"),
            # Ollama no entiende response_format=json_object (lo usaría PromptedOutput)
            profile=merge_profile(
                OllamaProvider.model_profile(nombre),
                OpenAIModelProfile(supports_json_object_output=False),
            ),
            settings={"temperature": 0, "max_tokens": 1500, "timeout": 120},
        )
    if settings.mode == "gemini":
        from google.genai.types import HttpRetryOptions
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider

        return GoogleModel(
            settings.gemini_model,
            provider=GoogleProvider(
                api_key=settings.gemini_api_key.get_secret_value(),
                # 429 por minuto o 503 pasajero: reintenta a los 10, 20 y 40 s.
                retry_options=HttpRetryOptions(
                    attempts=4,
                    initial_delay=10,
                    max_delay=40,
                    exp_base=2,
                    http_status_codes=[429, 503],
                ),
            ),
        )
    from pydantic_ai.models.openrouter import OpenRouterModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    return OpenRouterModel(
        settings.openrouter_model,
        provider=OpenRouterProvider(
            api_key=settings.openrouter_api_key.get_secret_value(),
            http_client=_cliente_con_reintentos(),
        ),
    )


def _cliente_con_reintentos():
    """Cliente HTTP que, ante 429 o 503, espera lo que pide el servidor (Retry-After) y reintenta."""
    import httpx2
    from pydantic_ai.retries import AsyncHTTPX2TenacityTransport, RetryConfig, wait_retry_after
    from tenacity import retry_if_exception_type, stop_after_attempt

    def validar(respuesta: httpx2.Response) -> None:
        if respuesta.status_code in (429, 503):
            respuesta.raise_for_status()

    transporte = AsyncHTTPX2TenacityTransport(
        config=RetryConfig(
            retry=retry_if_exception_type(httpx2.HTTPStatusError),
            wait=wait_retry_after(max_wait=40),
            stop=stop_after_attempt(4),
            reraise=True,
        ),
        validate_response=validar,
    )
    return httpx2.AsyncClient(transport=transporte, timeout=120)


def ruta_openai(settings: Settings) -> tuple[str, str, str]:
    """(URL base, clave, modelo) de la API compatible con OpenAI de la ruta elegida.

    Ollama, Gemini y OpenRouter hablan el mismo protocolo `/chat/completions`: es lo que usa
    el bucle sin framework de la sesión 1.
    """
    validar_ruta(settings)
    if settings.mode == "local":
        return settings.ollama_base_url.rstrip("/") + "/v1", "ollama", settings.ollama_model
    if settings.mode == "gemini":
        return (
            "https://generativelanguage.googleapis.com/v1beta/openai",
            settings.gemini_api_key.get_secret_value(),
            settings.gemini_model,
        )
    if settings.mode == "openrouter":
        return (
            "https://openrouter.ai/api/v1",
            settings.openrouter_api_key.get_secret_value(),
            settings.openrouter_model,
        )
    raise ValueError("MODE=offline no tiene API: usa local, gemini u openrouter.")
