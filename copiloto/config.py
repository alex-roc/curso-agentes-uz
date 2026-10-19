"""Una configuración para notebooks y scripts: las cuatro rutas de modelo."""

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
    ollama_model: str = "qwen3:4b-instruct"
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
        `copiloto-configurar` es lo que se usa, aunque tu terminal exporte otra clave."""
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


def describir_modelo(settings: Settings, offline: bool = False) -> str:
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
    """Sin cambio silencioso a proveedores de pago ni a modelos simulados."""
    if offline or settings.offline:
        from .simulado import modelo_simulado

        return modelo_simulado()
    validar_ruta(settings)
    if settings.mode == "local":
        from pydantic_ai.models.ollama import OllamaModel
        from pydantic_ai.profiles import merge_profile
        from pydantic_ai.profiles.openai import OpenAIModelProfile
        from pydantic_ai.providers.ollama import OllamaProvider

        nombre = settings.ollama_model
        return OllamaModel(
            nombre,
            provider=OllamaProvider(base_url=settings.ollama_base_url.rstrip("/") + "/v1"),
            profile=merge_profile(
                OllamaProvider.model_profile(nombre),
                OpenAIModelProfile(supports_json_object_output=False),
            ),
            settings={"temperature": 0, "max_tokens": 1500, "timeout": 120},
        )
    if settings.mode == "gemini":
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider

        return GoogleModel(
            settings.gemini_model,
            provider=GoogleProvider(api_key=settings.gemini_api_key.get_secret_value()),
        )
    from pydantic_ai.models.openrouter import OpenRouterModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    return OpenRouterModel(
        settings.openrouter_model,
        provider=OpenRouterProvider(api_key=settings.openrouter_api_key.get_secret_value()),
    )


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
