# Ollama: Mi copiloto en tu propio equipo

**Autoría: Alex Ojeda Copa y Lab TecnoSocial**

Ollama corre modelos de lenguaje **en tu computadora**: los datos no salen de tu equipo y no hay cuotas. Es la ruta de referencia del curso (`MODE=local`). Si tu equipo tiene poca RAM (8 GB o menos), empieza con [Gemini gratis](gemini.md) u [OpenRouter](openrouter.md) y deja esto para después.

## 1. Instalar y descargar el modelo

1. Descarga Ollama desde https://ollama.com/download e instálalo (macOS, Windows y Linux). Abre la aplicación o el servicio.
2. En la terminal (en Windows, Git Bash; ver [windows.md](windows.md)):

```bash
ollama --version
ollama pull gemma4:e2b      # unos 4,6 GB
ollama list                        # debe aparecer gemma4:e2b
```

`gemma4:e2b` necesita unos 6-8 GB de RAM libres. Cierra programas pesados si va lento.

## 2. Configurar el curso

En `.env` (copiado de `.env.example`):

```dotenv
MODE=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
```

Comprueba:

```bash
uv run python -m utilidades.doctor --live      # muestra el modelo y un saludo
```

Para que los notebooks usen el modelo en lugar del simulado, pon `COURSE_OFFLINE=0` en `.env` y reinicia el kernel.

## Problemas frecuentes

| Síntoma | Causa | Qué hacer |
|---|---|---|
| «conexión rechazada» o `ConnectError` | Ollama no está activo | Abre la aplicación Ollama (bandeja del sistema); solo si no hay servicio, `ollama serve` en otra terminal |
| `model not found` | No descargaste el modelo | `ollama pull gemma4:e2b` |
| La primera respuesta tarda mucho | El modelo se está cargando en memoria | Espera; las siguientes son más rápidas |
| Muy lento todo el tiempo | Poca RAM libre | Cierra programas o usa Gemini u OpenRouter |
| `ReadTimeout` | El modelo tardó más de 120 s | Reintenta; evita correr dos cosas pesadas a la vez |
