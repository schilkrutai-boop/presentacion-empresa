"""Chrome sin ventana (headless) para sacar el PDF, las capturas y la revisión de desbordes.

Busca Chrome, Chromium, Edge o Brave; también respeta la variable CHROME con la ruta
al ejecutable. Cada llamada usa un perfil temporal propio, así no choca con el
Chrome que la persona tenga abierto.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

RUTAS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
NOMBRES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"]


def encontrar() -> str | None:
    propia = os.environ.get("CHROME")
    if propia and Path(propia).exists():
        return propia
    for ruta in RUTAS:
        if Path(ruta).exists():
            return ruta
    for nombre in NOMBRES:
        encontrado = shutil.which(nombre)
        if encontrado:
            return encontrado
    return None


def _correr(chrome: str, args: list[str], timeout: int = 90) -> subprocess.CompletedProcess:
    perfil = tempfile.mkdtemp(prefix="chrome-deck-")
    base = [
        chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
        "--no-default-browser-check", "--disable-extensions", "--mute-audio",
        "--force-device-scale-factor=1", f"--user-data-dir={perfil}",
    ]
    try:
        return subprocess.run(base + args, capture_output=True, text=True, timeout=timeout)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)


def pdf(chrome: str, html: Path, salida: Path) -> bool:
    _correr(chrome, [
        "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={salida}",
        "--virtual-time-budget=6000", html.resolve().as_uri(),
    ], timeout=180)
    return salida.exists() and salida.stat().st_size > 0


def captura(chrome: str, url: str, salida: Path, ancho: int = 1920, alto: int = 1080) -> bool:
    _correr(chrome, [f"--window-size={ancho},{alto}", f"--screenshot={salida}", "--virtual-time-budget=4000", url])
    return salida.exists() and salida.stat().st_size > 0


def dom(chrome: str, url: str) -> str:
    """El HTML de la página después de correr sus scripts."""
    return _correr(chrome, ["--window-size=1920,1080", "--dump-dom", "--virtual-time-budget=5000", url]).stdout
