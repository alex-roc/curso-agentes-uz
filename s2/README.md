# Sesión 2 · Conocimiento, contexto y memoria

Jueves 22 de octubre de 2026. Le das a tu agente tres tipos de contexto: **conocimiento externo** (buscar y leer en la web, consultar una fuente de confianza), **conocimiento interno** (buscar en tus documentos por significado, con RAG, y citar la fuente) y **memoria** (continuar una conversación y recordar datos de la persona).

**Antes de empezar:** `git pull` y `uv sync` (hay librerías nuevas: `chromadb` y `langchain-text-splitters`). Si usas Ollama, descarga también el modelo de embeddings: `ollama pull embeddinggemma`.

## Cómo se conecta con la clase

En clase hay seis demos (**Demo 1** a **Demo 6**). El notebook alterna un **ejemplo mínimo** (el código de la demo) con un **ejercicio** que lo varía.

| Ejercicio | Qué haces | Se apoya en | Nivel |
|---|---|---|---|
| 1 · Leer una página | `WebFetch` recortado a 5000 caracteres | Demo 1 · Web | básico |
| 2 · Tu fuente: Open Library | `buscar_libro(titulo)` con autor, año y URL | Demo 2 · Fuente de confianza | medio |
| 3 · El tamaño del fragmento | `RecursiveCharacterTextSplitter` con trozos de 120 | Demo 3 · Fragmentar | básico |
| 4 · Tu propia base | indexar `datos/recetas/` en Chroma | Demo 3 · Indexar | medio |
| 5 · Asistente de cocina con citas | `buscar_recetas` como tool (RAG agéntico) | Demo 4 · RAG agéntico | medio |
| 6 · Memoria que sobrevive | `guardar` y `cargar` la conversación en JSON | Demo 5 · Conversación | medio |
| Reto · Recordar y olvidar | tools `recordar` y `olvidar` + instrucciones dinámicas | Demo 6 · Largo plazo | reto |

## Cómo trabajar

1. Abre la carpeta del repo en VS Code, abre `s2/01_conocimiento_y_memoria.ipynb`, elige el kernel `.venv` y ejecuta con Shift+Enter.
2. Cada ejercicio tiene `# TODO` y una celda de autocorrección: **✅** pasa, **⏳** falta algo (te dice qué). Un ⏳ no rompe el notebook.

- **Simulado (por defecto):** `COURSE_OFFLINE=1` en `.env`. **No es IA**: elige tools por parecido de palabras. Chroma usa su modelo de embeddings pequeño (en inglés; se descarga una vez, unos 80 MB).
- **IA real:** `COURSE_OFFLINE=0` en `.env` y *Restart* del kernel. Con Ollama los embeddings son `embeddinggemma`; con Gemini, `gemini-embedding-001` (gratis, con tu clave).
- La búsqueda web, Wikipedia y Open Library necesitan internet. El notebook crea `conversaciones/` y `recuerdos.txt` en esta carpeta.
- **Entrega** (se revisa al inicio de la siguiente sesión): tu notebook con los ejercicios y, si puedes, las salidas de una ejecución con IA real.
