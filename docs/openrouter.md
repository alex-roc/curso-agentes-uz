# OpenRouter gratis: modelos abiertos sin instalar nada

**Autoría: Alex Ojeda Copa y Lab TecnoSocial**

OpenRouter es un intermediario: con una sola clave se accede a cientos de modelos de distintos proveedores. Los que terminan en **`:free`** no cobran por token. Es la tercera ruta para la **sesión 1**, junto con [Gemini gratis](gemini.md) y Ollama local ([ollama.md](ollama.md)). Sirve, además, para comparar modelos abiertos (Qwen, Gemma, Nemotron…) sin descargarlos.

| Ruta | `.env` | Datos |
|---|---|---|
| Ollama local (referencia) | `MODE=local` | No salen de tu equipo |
| Gemini gratis | `MODE=gemini` | Viajan a Google, que puede usarlos para mejorar sus productos |
| **OpenRouter `:free`** | `MODE=openrouter` | Viajan a OpenRouter y al proveedor del modelo; revisa tu configuración de privacidad |
| Simulado | `MODE=offline` | Sin IA real |

## 1. Crear la cuenta y la clave (5 minutos)

1. Crea una cuenta en **https://openrouter.ai** (con Google o correo).
2. En **https://openrouter.ai/keys**, pulsa **Create Key**, ponle un nombre (por ejemplo `mi-copiloto`) y copia la clave (es una cadena larga). Solo se muestra una vez.
3. **No hace falta comprar créditos** para los modelos `:free`. Sin compras, el límite es de 20 peticiones por minuto y **50 por día**. Si algún día compras 10 USD en créditos, sube a 1000 por día ([límites oficiales](https://openrouter.ai/docs/api-reference/limits)).
4. Revisa **https://openrouter.ai/settings/privacy**. Algunos modelos gratuitos solo están disponibles con proveedores que pueden registrar o entrenar con lo que envías. Si un modelo `:free` responde que no hay proveedores disponibles, es por esa configuración. Actívala solo si aceptas esa condición; por eso usamos datos ficticios.

## 2. Elegir un modelo `:free` con tools

El catálogo gratuito cambia cada semana, por eso el curso no fija un modelo. Míralos en **https://openrouter.ai/models?q=free** (filtra por *tools* en «Supported Parameters») y copia el ID exacto. Candidatos de la lista del 18 de octubre de 2026: `nvidia/nemotron-3-super-120b-a12b:free`, `google/gemma-4-31b-it:free` o `xingchen-agi/xing4.0-29b-a4b:free`. Que aparezca en la lista **no garantiza** que use bien las tools: pruébalo.

## 3. Configurar el curso

```dotenv
MODE=openrouter
OPENROUTER_API_KEY=tu_clave
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

```bash
uv run python -m utilidades.doctor --live        # muestra el modelo y un saludo
uv run python s1/chat_terminal.py    # pregunta «¿qué hora es?»: ¿usa la tool?
```

Estos materiales **rechazan** un `OPENROUTER_MODEL` que no termine en `:free`, para que nadie gaste dinero por error.

## 4. Cuotas: 50 peticiones al día se acaban rápido

- **Un mensaje no es una petición.** Un pedido con tools hace entre 2 y 4 llamadas al modelo; 50 por día dan para unas 15 preguntas con herramientas.
- Si ves `429`, espera o cambia de modelo. Un modelo gratuito también puede estar saturado: OpenRouter devuelve 429 por capacidad del proveedor. **No** lo arregles con bucles de reintento.
- Un saldo negativo bloquea incluso los modelos gratuitos (`402`).

## Problemas frecuentes

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `MODE=openrouter requiere OPENROUTER_MODEL ... :free` | ID vacío o de pago | Copia un ID de https://openrouter.ai/models?q=free |
| `Falta OPENROUTER_API_KEY` | `.env` sin clave | Crea una en https://openrouter.ai/keys |
| `404` o «No endpoints found» | Modelo retirado o bloqueado por tu configuración de privacidad | Elige otro ID o revisa https://openrouter.ai/settings/privacy |
| `429` | 20 por minuto o 50 por día, o proveedor saturado | Espera, cambia de modelo o usa `MODE=offline` |
| `tool_use_failed` o el agente no llama tools | El modelo no maneja bien las herramientas | Cambia de modelo: es material para la clase de selección de modelos |
