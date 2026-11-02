#!/usr/bin/env python3
"""Busca el logo de una empresa en su sitio web y deja los candidatos para elegir.

Uso:
  python3 buscar_logo.py <url> [<url> …] --carpeta <carpeta de la empresa>

Cada <url> puede ser la página de la empresa (se buscan los logos que declara: el
«logo» de schema.org, los <svg> e <img> marcados como logo, og:image y los íconos) o
directamente la dirección de una imagen. Descarga hasta 12 candidatos a
<carpeta>/logo-candidatos/, muestra su tipo y tamaño, y arma candidatos.png con cada
uno sobre fondo blanco y sobre fondo oscuro, para elegir mirando.

Después: copia el elegido como <carpeta>/logo.<ext> (y, si hay una versión clara para
fondos oscuros, como logo-claro.<ext>).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import navegador

AGENTE = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
EXT = {"image/svg+xml": "svg", "image/png": "png", "image/jpeg": "jpg", "image/gif": "gif",
       "image/webp": "webp", "image/x-icon": "ico"}


def bajar(url: str, maximo: int = 3_000_000) -> tuple[bytes, str]:
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "*/*", "Accept-Language": "es-CL,es;q=0.9"})
    with urllib.request.urlopen(pedido, timeout=20) as r:
        return r.read(maximo + 1)[:maximo], r.geturl()


def tipo_de(datos: bytes) -> str | None:
    if datos.startswith(b"\x89PNG"):
        return "image/png"
    if datos.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if datos.startswith(b"GIF8"):
        return "image/gif"
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    if datos[:4] == b"\x00\x00\x01\x00":
        return "image/x-icon"
    cabeza = datos[:4000].lower()
    if b"<svg" in cabeza and b"<html" not in cabeza:
        return "image/svg+xml"
    return None


def medidas(datos: bytes, tipo: str) -> str:
    try:
        if tipo == "image/png":
            return "%d×%d" % struct.unpack(">II", datos[16:24])
        if tipo == "image/gif":
            return "%d×%d" % struct.unpack("<HH", datos[6:10])
        if tipo == "image/jpeg":
            i = 2
            while i < len(datos) - 9:
                if datos[i] != 0xFF:
                    i += 1
                    continue
                marca = datos[i + 1]
                if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):
                    alto, ancho = struct.unpack(">HH", datos[i + 5:i + 9])
                    return f"{ancho}×{alto}"
                i += 2 + struct.unpack(">H", datos[i + 2:i + 4])[0]
        if tipo == "image/webp":
            if datos[12:16] == b"VP8X":
                return f"{1 + int.from_bytes(datos[24:27], 'little')}×{1 + int.from_bytes(datos[27:30], 'little')}"
            if datos[12:16] == b"VP8 ":
                ancho, alto = struct.unpack("<HH", datos[26:30])
                return f"{ancho & 0x3FFF}×{alto & 0x3FFF}"
        if tipo == "image/x-icon":
            return f"{datos[6] or 256}×{datos[7] or 256}"
        if tipo == "image/svg+xml":
            texto = datos[:3000].decode("utf-8", "ignore")
            vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', texto)
            if vb:
                return f"vector {float(vb.group(1)):.0f}×{float(vb.group(2)):.0f}"
            return "vector"
    except (struct.error, IndexError):
        pass
    return "?"


def con_y_sin_www(url: str) -> list[str]:
    partes = urllib.parse.urlparse(url)
    host = partes.netloc
    otro = host[4:] if host.startswith("www.") else "www." + host
    return [url, partes._replace(netloc=otro).geturl()]


def candidatos_de_pagina(url: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Devuelve ([(url_imagen, origen)], [(svg_en_línea, origen)]). Si el sitio falla (por ejemplo, un
    certificado que no calza con «www.»), prueba la otra forma del dominio."""
    error = None
    for intento in con_y_sin_www(url):
        try:
            datos, final = bajar(intento)
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError) as e:
            error = e
    else:
        raise error
    pagina = datos.decode("utf-8", "ignore")
    abs_ = lambda u: urllib.parse.urljoin(final, html.unescape(u.strip()))
    urls: list[tuple[str, str]] = []

    for bloque in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', pagina, re.S | re.I):
        try:
            texto = json.dumps(json.loads(bloque))
        except ValueError:
            texto = bloque
        for m in re.finditer(r'"logo"\s*:\s*(?:\{[^{}]*?"url"\s*:\s*)?"([^"]+)"', texto):
            urls.append((abs_(m.group(1)), "schema.org «logo»"))

    for etiqueta in re.findall(r"<img\b[^>]*>", pagina, re.I):
        attrs = dict((k.lower(), v) for k, _, v in re.findall(r'([\w:-]+)\s*=\s*(["\'])(.*?)\2', etiqueta, re.S))
        pista = " ".join(attrs.get(k, "") for k in ("src", "alt", "class", "id", "data-src", "title")).lower()
        if "logo" not in pista and "marca" not in pista and "brand" not in pista:
            continue
        src = attrs.get("data-src") or attrs.get("data-lazy-src") or attrs.get("src") or ""
        if attrs.get("srcset") and not src.lower().endswith(".svg"):
            src = attrs["srcset"].split(",")[-1].strip().split(" ")[0] or src
        if src and not src.startswith("data:"):
            urls.append((abs_(src), f"<img> «{html.unescape(attrs.get('alt') or attrs.get('class') or '')[:30]}»"))

    for m in re.finditer(r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)', pagina, re.I):
        urls.append((abs_(m.group(1)), "og:image (suele ser una foto, no el logo)"))
    for etiqueta in re.findall(r"<link\b[^>]*>", pagina, re.I):
        rel = re.search(r'rel=["\']([^"\']+)', etiqueta, re.I)
        href = re.search(r'href=["\']([^"\']+)', etiqueta, re.I)
        if rel and href and any(k in rel.group(1).lower() for k in ("icon", "apple-touch", "mask-icon")):
            urls.append((abs_(href.group(1)), f"ícono ({rel.group(1)})"))

    en_linea: list[tuple[str, str]] = []
    for m in re.finditer(r"<svg\b.*?</svg>", pagina, re.S | re.I):
        antes = pagina[max(0, m.start() - 400):m.start()].lower()
        apertura = pagina[m.start():m.start() + 300].lower()
        if "logo" in apertura or 'class="logo' in antes or "logo" in antes[-160:]:
            svg = m.group(0)
            if "xmlns=" not in svg[:300]:
                svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            if len(svg) > 300 and "<use" not in svg:
                en_linea.append((svg, "<svg> en la página"))
        if len(en_linea) >= 3:
            break

    dominio = urllib.parse.urlparse(final).netloc
    urls.append((f"https://www.google.com/s2/favicons?domain={dominio}&sz=256", "ícono de Google (último recurso)"))
    return urls, en_linea


def dominio(url: str) -> str:
    host = urllib.parse.urlparse(url if "://" in url else "https://" + url).netloc.lower()
    return ".".join(host.split(".")[-2:])


def main() -> None:
    ap = argparse.ArgumentParser(description="Busca el logo de una empresa en su sitio.")
    ap.add_argument("urls", nargs="+", help="página de la empresa o dirección directa de una imagen")
    ap.add_argument("--carpeta", required=True, help="carpeta de la empresa (se crea logo-candidatos/ adentro)")
    ap.add_argument("--max", type=int, default=12)
    ap.add_argument("--sumar", action="store_true", help="agrega a los candidatos que ya hay en vez de reemplazarlos")
    args = ap.parse_args()

    destino = Path(args.carpeta).expanduser() / "logo-candidatos"
    destino.mkdir(parents=True, exist_ok=True)
    previos = sorted(destino.glob("cand-*"))
    if not args.sumar:
        for viejo in previos:
            viejo.unlink()
        previos = []

    urls: list[tuple[str, str]] = []
    en_linea: list[tuple[str, str]] = []
    for url in args.urls:
        if not re.match(r"https?://", url):
            url = "https://" + url
        if re.search(r"\.(svg|png|jpe?g|webp|gif|ico)(\?|$)", url, re.I):
            urls.append((url, "dirección directa"))
            continue
        try:
            u, s = candidatos_de_pagina(url)
            urls += u
            en_linea += s
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError) as e:
            print(f"NO PUDE LEER {url}: {e}. Abre el sitio en el navegador, copia la dirección del logo y pásala directo "
                  "(con --sumar para no borrar estos candidatos).")
            host = re.sub(r"^www\.", "", urllib.parse.urlparse(url).netloc)
            urls.append((f"https://www.google.com/s2/favicons?domain={host}&sz=256", "ícono de Google (último recurso)"))

    vistos, filas = set(), []
    for archivo in previos:
        datos = archivo.read_bytes()
        tipo = tipo_de(datos)
        if tipo:
            filas.append((archivo, tipo, medidas(datos, tipo), "de una búsqueda anterior", ""))
    for svg, origen in en_linea:
        archivo = destino / f"cand-{len(filas) + 1:02d}.svg"
        archivo.write_text(svg, encoding="utf-8")
        filas.append((archivo, "image/svg+xml", medidas(svg.encode(), "image/svg+xml"), origen, "(en la página)"))
    for url, origen in urls:
        if len(filas) >= args.max or url in vistos:
            continue
        vistos.add(url)
        try:
            datos, _ = bajar(url)
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError):
            continue
        tipo = tipo_de(datos)
        if not tipo:
            continue
        if dominio(url) != dominio(args.urls[0]) and "google.com/s2" not in url and origen != "dirección directa":
            origen += " · de otro sitio: ¿es de la empresa?"
        archivo = destino / f"cand-{len(filas) + 1:02d}.{EXT[tipo]}"
        archivo.write_bytes(datos)
        filas.append((archivo, tipo, medidas(datos, tipo), origen, url))

    if not filas:
        sys.exit("Sin candidatos. Busca el logo con el navegador (o en sus redes) y pasa la dirección de la imagen.")

    print(f"{len(filas)} candidatos en {destino}")
    for archivo, tipo, tam, origen, url in filas:
        print(f"  {archivo.name:12} {EXT[tipo]:4} {tam:18} {archivo.stat().st_size // 1024:>5} KB  {origen}  {url[:90]}")

    tarjetas = "".join(
        f'<figure><div class="f claro"><img src="{a.name}"></div><div class="f oscuro"><img src="{a.name}"></div>'
        f'<figcaption>{a.name} · {html.escape(t)} · {html.escape(o[:40])}</figcaption></figure>'
        for a, _, t, o, _ in filas)
    hoja = destino / "candidatos.html"
    hoja.write_text(
        '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#E3E7E5;font:14px ui-monospace,Menlo,monospace}'
        'main{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:18px}figure{margin:0;background:#fff;border-radius:10px;overflow:hidden}'
        '.f{height:150px;display:grid;place-items:center;padding:16px}.claro{background:#fff}.oscuro{background:#111413}'
        'img{max-width:90%;max-height:110px}figcaption{padding:8px 10px;color:#282B2C}</style>'
        f'<main>{tarjetas}</main>', encoding="utf-8")
    chrome = navegador.encontrar()
    if chrome:
        filas_hoja = -(-len(filas) // 3)
        png = destino / "candidatos.png"
        if navegador.captura(chrome, hoja.resolve().as_uri(), png, 1400, 18 + filas_hoja * 470):
            print(f"Míralos en {png} (cada uno sobre blanco y sobre oscuro).")
    else:
        print(f"Sin Chrome para la hoja de candidatos: abre {hoja} en el navegador.")


if __name__ == "__main__":
    main()
