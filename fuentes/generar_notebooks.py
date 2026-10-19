#!/usr/bin/env python3
"""Regenera los .ipynb de s0/, s1/… desde fuentes/sN/*.py (marcadores # %%), solo con stdlib.

Uso: python3 fuentes/generar_notebooks.py
Los outputs se descartan a propósito: las credenciales y respuestas personales no
deben quedar versionadas. Los IDs dependen del contenido y no del entorno.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def convertir(path: Path) -> dict:
    cells = []
    kind = None
    lines: list[str] = []

    def cerrar() -> None:
        if kind is None:
            return
        source = "".join(lines).strip("\n") + "\n"
        if kind == "markdown":
            source = (
                "\n".join(
                    line[2:] if line.startswith("# ") else line[1:] if line == "#" else line
                    for line in source.splitlines()
                )
                + "\n"
            )
        identity = f"{path.stem}:{len(cells)}:{source}".encode()
        cell = {
            "cell_type": kind,
            "id": hashlib.sha256(identity).hexdigest()[:12],
            "metadata": {},
            "source": source.splitlines(keepends=True),
        }
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("# %%"):
            cerrar()
            kind = "markdown" if "[markdown]" in line else "code"
            lines = []
        elif kind is not None:
            lines.append(line)
    cerrar()
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    for source in sorted((ROOT / "fuentes").glob("s*/*.py")):
        destination = ROOT / source.parent.name / source.with_suffix(".ipynb").name
        destination.write_text(
            json.dumps(convertir(source), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
