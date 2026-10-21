# Instalación en Windows (Git Bash)

**Autoría: Alex Ojeda Copa y Lab TecnoSocial**

Todo funciona nativamente en Windows 10 y 11, sin WSL. Para que **los comandos sean los mismos que en macOS y Linux**, trabaja en **Git Bash**, la terminal bash que viene con Git for Windows.

## 1. Instalar (una vez, unos 20 minutos)

1. **Git for Windows** (incluye Git Bash): https://git-scm.com/download/win, con las opciones por defecto.
2. **uv**: abre *PowerShell* una sola vez y ejecuta `winget install --id astral-sh.uv -e`. Sin winget: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
3. **VS Code** (recomendado) con las extensiones *Python* y *Jupyter*.
4. Opcional, para IA local: Ollama ([ollama.md](ollama.md)).

**Elige Git Bash como terminal.** En VS Code: `Ctrl+Shift+P` → «Terminal: Select Default Profile» → **Git Bash**, y abre una terminal nueva. Cierra y vuelve a abrir la terminal después de instalar, para que tome el PATH. Comprueba `uv --version` y `git --version`.

> **Clona fuera de OneDrive.** Las carpetas sincronizadas (Escritorio y Documentos, si OneDrive está activo) dan problemas con archivos que cambian. Usa, por ejemplo, `C:\cursos`, que en Git Bash es `/c/cursos`.

## 2. Descargar el repositorio e instalar

**Atajo:** con Git Bash, `bash instalar.sh` dentro del repositorio instala uv si falta, hace `uv sync` y lanza el configurador (y desde PowerShell: `powershell -ExecutionPolicy Bypass -File instalar.ps1`). Lo de abajo es el camino manual.

```bash
mkdir -p /c/cursos && cd /c/cursos
git clone https://github.com/alex-roc/curso-agentes-uz.git
cd curso-agentes-uz
uv sync
uv run python -m utilidades.configurar
```

## 3. Reglas útiles

1. **Siempre `uv run ...`.** No escribas `python` a secas ni actives el entorno a mano.
2. **Rutas:** `C:\cursos` se escribe `/c/cursos`; `~` es tu carpeta de usuario.
3. **Notebooks en VS Code:** abre la carpeta del repositorio, abre el `.ipynb` y elige *Select Kernel → Python Environments → `.venv`* (en Windows es `.venv\Scripts\python.exe`; VS Code lo detecta solo). Tras cambiar `.env`, pulsa **Restart**.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `uv: command not found` | La terminal se abrió antes de instalar uv | Cierra y abre la terminal (o reinicia VS Code) |
| La terminal de VS Code abre PowerShell | No se cambió el perfil | `Ctrl+Shift+P` → «Terminal: Select Default Profile» → Git Bash |
| Un notebook usa otro Python | Kernel equivocado | Elige el kernel del `.venv` del repositorio |
| Caracteres raros en la terminal | Codificación | Usa Git Bash en VS Code o Windows Terminal |
