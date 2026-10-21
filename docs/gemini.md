# Gemini gratis: Mi copiloto sin instalar un modelo

**Autoría: Alex Ojeda Copa y Lab TecnoSocial**

Para la **sesión 1** basta con una clave gratuita de Gemini (o de OpenRouter, ver [openrouter.md](openrouter.md)). Así todos prueban un agente real desde el primer día, aunque su computadora no pueda correr Ollama todavía. La ruta local (Ollama) sigue siendo la referencia del curso y se instala con calma ([ollama.md](ollama.md)).

| Ruta | Qué necesitas | Cuándo |
|---|---|---|
| `MODE=gemini` | Una cuenta de Google y una clave gratuita de AI Studio | Sesión 1, equipos con poca RAM, mientras instalas Ollama |
| `MODE=openrouter` | Una cuenta de OpenRouter y un modelo `:free` ([openrouter.md](openrouter.md)) | Modelos abiertos sin descargarlos; 50 peticiones por día |
| `MODE=local` | Ollama y unos 3 GB de modelo | Referencia del curso; los datos no salen de tu equipo |
| `MODE=offline` | Nada | Plan B: ciclo del agente sin IA real |

## 1. Crear la clave (5 minutos, sin tarjeta)

1. Entra a **https://aistudio.google.com/apikey** con tu cuenta de Google.
2. Acepta los términos. AI Studio crea un proyecto y una clave por defecto. Si no aparece, pulsa **Create API key**.
3. Copia la clave. Trátala como una contraseña: no la pegues en chats ni la subas a GitHub.

La capa gratuita es la predeterminada en las cuentas nuevas y **no pide tarjeta**. Google solo pide facturación para pasar al plan de pago, que exige vincular una cuenta y prepagar un mínimo de 5 USD. **No vincules facturación:** si lo haces, el proyecto pasa a pago y deja de ser gratis. Si AI Studio te ofrece «Upgrade» o «Set up billing», ignóralo; la clave funciona sin eso.

Requisitos de Google: tener **18 años o más** y estar en un país habilitado (**Bolivia lo está**). Fuentes: [regiones disponibles](https://ai.google.dev/gemini-api/docs/available-regions), [facturación](https://ai.google.dev/gemini-api/docs/billing) y [términos](https://ai.google.dev/gemini-api/terms).

## 2. Configurar el curso

En `.env` (copiado de `.env.example`):

```dotenv
MODE=gemini
GEMINI_API_KEY=tu_clave
GEMINI_MODEL=gemini-3.5-flash-lite
```

Para que los notebooks usen la IA real, pon también `COURSE_OFFLINE=0` en `.env`. Comprueba y conversa:

```bash
uv run python -m utilidades.doctor --live          # muestra el modelo y un saludo
```

Para volver a Ollama, cambia `MODE=local`. No hace falta borrar la clave.

## 3. Qué modelo elegir

Modelos de texto con capa gratuita según la [página de precios](https://ai.google.dev/gemini-api/docs/pricing) (revisada el 18 de octubre de 2026):

| Modelo | Para qué |
|---|---|
| `gemini-3.5-flash-lite` | **Predeterminado del curso.** Rápido y barato en cuota; Google lo recomienda para proyectos nuevos |
| `gemini-3.8-flash` | Más capaz con varias tools y pasos; gasta más cuota |
| `gemini-3.1-flash-lite`, `gemini-3.6-flash` | Alternativas si uno de los anteriores devuelve 429 |

Los modelos **Pro** no tienen capa gratuita. Google cambia este catálogo con frecuencia: si un modelo desaparece, revisa la página de precios y cambia solo `GEMINI_MODEL`. Ese cambio de una variable es justamente lo que se enseña en la sesión 1 al elegir modelos.

## 4. Límites y error 429

- Los límites son **por proyecto**, no por clave, y dependen del modelo. Míralos en **https://aistudio.google.com/rate-limit**.
- La cuota diaria se reinicia a medianoche del Pacífico, que son las 03:00 en Bolivia.
- **Un mensaje no es una petición.** Un pedido con tools hace entre 2 y 4 llamadas al modelo; un flujo multiagente de la S5, más.
- Si ves `429`, esperaste poco entre pedidos o se acabó la cuota del día. Espera un minuto, cambia `GEMINI_MODEL` o sigue con `MODE=offline`. **No** lo arregles con bucles de reintento.

## 5. Privacidad: solo datos ficticios

En la capa gratuita, **Google usa lo que envías y lo que responde el modelo para mejorar sus productos, y personas pueden revisarlo** ([términos, «Unpaid Services»](https://ai.google.dev/gemini-api/terms)). Por eso:

- Con `MODE=gemini` gratis, trabaja con los datos ficticios de los materiales.
- No pegues datos personales ni de terceros mientras uses la capa gratuita. Para eso usa Ollama: los datos no salen de tu equipo.

Es un buen ejemplo de un criterio de la sesión 1: elegir modelo también es elegir **a dónde viajan tus datos**.

## Problemas frecuentes

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `Falta GEMINI_API_KEY` | `.env` sin la clave o `MODE=gemini` sin clave | Pega la clave en `.env`, sin comillas ni espacios |
| `400` o `403 API key not valid` | Clave mal copiada o revocada | Copia de nuevo desde AI Studio |
| `404 model not found` | Modelo retirado o mal escrito | Usa uno de la tabla del punto 3 |
| `429 RESOURCE_EXHAUSTED` | Cuota por minuto o por día | Espera, cambia de modelo o usa `MODE=offline` |
| `429 ... spending cap` | El proyecto tiene facturación y llegó a su tope | Usa un proyecto sin facturación (capa gratuita) |
| Tienes otra `GEMINI_API_KEY` en el entorno | Una variable de entorno gana sobre `.env` | Ejecuta con `env -u GEMINI_API_KEY ...` o bórrala de tu entorno |
| El agente no usa tools o inventa | Modelo demasiado pequeño para el pedido | Prueba `gemini-3.8-flash` y compara; es material para la sesión 1 |
