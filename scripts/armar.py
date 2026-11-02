#!/usr/bin/env python3
"""Arma la presentación de Fixero para una empresa, con el diseño del deck Fixero × Scanavini.

Uso:
  python3 armar.py <carpeta o empresa.json> [--pdf] [--revisar] [--salida CARPETA]

Lee empresa.json (el formato está en referencias/empresa.ejemplo.json), el logo que
indica y los recursos de la skill (fuentes, logos de Fixero, íconos Phosphor, foto de
portada), y escribe junto al JSON:
  Fixero-<Empresa>.html   un solo archivo, sin dependencias: se abre en cualquier navegador
  Fixero-<Empresa>.pdf    con --pdf (una diapositiva por página, 1920×1080)
  revision/NN.png         con --revisar: una captura por diapositiva, y avisa qué
                          diapositivas tienen texto que se sale de su espacio
  fuentes.md              las fuentes de cada dato de la empresa y lo que falta confirmar

Termina con código 1 si falta un dato obligatorio, un ícono no existe o (con --revisar)
algo se sale de su espacio.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import difflib
import html
import json
import re
import sys
import unicodedata
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import navegador

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
PLANTILLA = SKILL / "plantilla"
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
         "Septiembre", "Octubre", "Noviembre", "Diciembre"]


# ───────────────────────── Lectura y validación del JSON ─────────────────────────

class Datos:
    """Lee empresa.json por rutas («portada.titular», «beneficios.items[2].texto»),
    escapa el texto y junta errores (bloquean) y avisos (largos sugeridos)."""

    def __init__(self, raiz: dict):
        self.raiz = raiz
        self.errores: list[str] = []
        self.avisos: list[str] = []
        self.nombre = ""  # nombre de la empresa ya escapado; t() lo deja en una sola línea

    def valor(self, ruta: str):
        obj = self.raiz
        for parte in re.findall(r"[^.\[\]]+", ruta):
            if isinstance(obj, list):
                i = int(parte)
                obj = obj[i] if i < len(obj) else None
            elif isinstance(obj, dict):
                obj = obj.get(parte)
            else:
                return None
            if obj is None:
                return None
        return obj

    def hay(self, ruta: str) -> bool:
        return self.valor(ruta) not in (None, "", [], {})

    def crudo(self, ruta: str, limite: int | None = None, opcional=False, defecto: str | None = None) -> str:
        v = self.valor(ruta)
        if v in (None, ""):
            if defecto is not None:
                v = defecto
            elif opcional:
                return ""
            else:
                self.errores.append(f"Falta «{ruta}».")
                return ""
        if not isinstance(v, (str, int, float)):
            self.errores.append(f"«{ruta}» debe ser texto.")
            return ""
        v = re.sub(r"[ \t\r\n]+", " ", str(v)).strip()
        if limite and len(v) > limite:
            self.avisos.append(f"«{ruta}» tiene {len(v)} caracteres (sugerido: hasta {limite}): «{v[:70]}…»")
        return v

    def t(self, ruta: str, limite: int | None = None, opcional=False, defecto: str | None = None, attr=False) -> str:
        """Texto escapado. Para atributos HTML usa attr=True (sin el <span> que evita cortar el nombre)."""
        texto = html.escape(self.crudo(ruta, limite, opcional, defecto))
        if not attr and " " in self.nombre:
            texto = texto.replace(self.nombre, f'<span class="nw">{self.nombre}</span>')
        return texto

    def lista(self, ruta: str, minimo: int, maximo: int, opcional=False) -> list[str]:
        v = self.valor(ruta)
        if not v:
            if not opcional:
                self.errores.append(f"Falta la lista «{ruta}» ({minimo} a {maximo} elementos).")
            return []
        if not isinstance(v, list):
            self.errores.append(f"«{ruta}» debe ser una lista.")
            return []
        if not minimo <= len(v) <= maximo:
            self.errores.append(f"«{ruta}» tiene {len(v)} elementos; deben ser entre {minimo} y {maximo}.")
        return [f"{ruta}[{i}]" for i in range(min(len(v), maximo))]

    def icono(self, ruta: str, defecto: str | None = None) -> str:
        nombre = self.crudo(ruta, opcional=defecto is not None, defecto=defecto)
        return icono(nombre, self, ruta)


_ICONOS: dict[str, str] = {}


def icono(nombre: str, d: Datos | None = None, ruta: str = "") -> str:
    if nombre in _ICONOS:
        return _ICONOS[nombre]
    archivo = ASSETS / "iconos" / f"{nombre}.svg"
    if not archivo.exists():
        if d is not None:
            todos = [p.stem for p in (ASSETS / "iconos").glob("*.svg")]
            parecidos = difflib.get_close_matches(nombre, todos, n=4, cutoff=0.5)
            d.errores.append(f"El ícono «{nombre}» ({ruta}) no existe en assets/iconos."
                             + (f" Parecidos: {', '.join(parecidos)}." if parecidos else ""))
        return ""
    _ICONOS[nombre] = svg_limpio(archivo.read_text(), "i")
    return _ICONOS[nombre]


def svg_limpio(svg: str, clase: str) -> str:
    svg = re.sub(r"<\?xml.*?\?>", "", svg)
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r'\s(id|role|aria-label)="[^"]*"', "", svg)
    return svg.replace("<svg ", f'<svg class="{clase}" aria-hidden="true" focusable="false" ', 1).strip()


def data_uri(ruta: Path) -> str:
    datos = ruta.read_bytes()
    if datos.startswith(b"\x89PNG"):
        tipo = "image/png"
    elif datos.startswith(b"\xff\xd8"):
        tipo = "image/jpeg"
    elif datos.startswith(b"GIF8"):
        tipo = "image/gif"
    elif datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        tipo = "image/webp"
    elif b"<svg" in datos[:4000].lower():
        tipo = "image/svg+xml"
    elif ruta.suffix.lower() == ".woff2":
        tipo = "font/woff2"
    elif ruta.suffix.lower() == ".ttf":
        tipo = "font/ttf"
    else:
        raise ValueError(f"{ruta.name}: formato no reconocido (usa SVG, PNG, JPG, WebP o GIF)")
    return f"data:{tipo};base64," + base64.b64encode(datos).decode()


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "-".join(re.findall(r"[A-Za-z0-9]+", texto)) or "Empresa"


def iniciales(nombre: str) -> str:
    partes = [p for p in re.split(r"[\s.]+", nombre) if p]
    return "".join(p[0].upper() for p in partes[:2]) or "?"


# ───────────────────────── Piezas comunes ─────────────────────────

class Deck:
    def __init__(self, d: Datos, base: Path):
        self.d = d
        self.base = base
        self.n_attr = html.escape(d.crudo("empresa.nombre", 40))
        d.nombre = self.n_attr
        self.n = d.t("empresa.nombre")
        self.trabajador = d.crudo("empresa.trabajador", 20, defecto="técnico")
        self.logo = self._logo("empresa.logo")
        self.logo_claro = self._logo("empresa.logo_claro")
        self.en_oscuro = d.crudo("empresa.logo_en_oscuro", defecto="chip")
        self.en_naranja = d.crudo("empresa.logo_en_naranja", defecto="chip")
        if self.en_oscuro not in ("chip", "blanco"):
            d.errores.append("«empresa.logo_en_oscuro» debe ser «chip» o «blanco».")
        if self.en_naranja not in ("chip", "directo"):
            d.errores.append("«empresa.logo_en_naranja» debe ser «chip» o «directo».")
        self.numero = 0
        self.fixero = {k: svg_limpio((ASSETS / "logos" / f"{v}.svg").read_text(), "logo " + k) for k, v in {
            "blanco": "fixero-mandarina-blanco", "grafito": "fixero-mandarina-grafito", "pajaro": "fixero-pajaro-naranja"}.items()}

    def _logo(self, ruta: str) -> str:
        nombre = self.d.crudo(ruta, opcional=True)
        if not nombre:
            return ""
        archivo = (self.base / nombre).resolve()
        if not archivo.exists():
            self.d.errores.append(f"«{ruta}»: no encuentro el archivo {archivo}.")
            return ""
        try:
            uri = data_uri(archivo)
        except ValueError as e:
            self.d.errores.append(f"«{ruta}»: {e}")
            return ""
        if archivo.stat().st_size > 400_000:
            self.d.avisos.append(f"El logo {archivo.name} pesa {archivo.stat().st_size // 1024} KB; busca uno más liviano (SVG o PNG de hasta ~300 KB).")
        return uri

    def logo_empresa(self, fondo: str) -> str:
        """fondo: «oscuro» (portada), «naranja» (cierre) o «mockup» (dentro de un teléfono)."""
        alt = f'alt="{self.n_attr}"'
        if not self.logo:
            # En la caja chica de los teléfonos el nombre puede ir en dos líneas.
            return f'<span class="wordmark">{self.n_attr if fondo == "mockup" else self.n}</span>'
        if fondo == "mockup":
            return f'<img src="{self.logo}" {alt}>'
        if fondo == "oscuro":
            if self.logo_claro:
                return f'<span class="co"><img src="{self.logo_claro}" {alt}></span>'
            return f'<span class="co {self.en_oscuro}"><img src="{self.logo}" {alt}></span>'
        clase = "chip" if self.en_naranja == "chip" else ""
        return f'<span class="co {clase}"><img src="{self.logo}" {alt}></span>'

    def eyebrow(self, texto: str) -> str:
        self.numero += 1
        return f'<div class="eyebrow"><b>{self.numero:02d}</b><span>{texto}</span></div>'

    def pie(self) -> str:
        return f'<footer class="foot"><span class="brand">{self.fixero["pajaro"]}Fixero × {self.n}</span><span class="pg"></span></footer>'

    def filas(self, ruta: str, minimo: int, maximo: int, lim_titulo: int, lim_texto: int) -> str:
        d = self.d
        return "\n".join(
            f'<li class="row">{d.icono(r + ".icono")}<div><h3>{d.t(r + ".titulo", lim_titulo)}</h3>'
            f'<p class="body">{d.t(r + ".texto", lim_texto)}</p></div></li>'
            for r in d.lista(ruta, minimo, maximo))


SB = ('<div class="sb"><span>9:41</span><span class="island"></span><span class="ic"><span class="sig">'
      '<i style="height:4px"></i><i style="height:6px"></i><i style="height:8px"></i><i style="height:11px"></i>'
      '</span><span class="bat"></span></span></div>')

ESTADOS = {
    "terminado": ("exito", "Terminado"), "sin_asignar": ("alerta", "Sin asignar"), "en_camino": ("acento", "En camino"),
    "asignado": ("info", "Asignado"), "trabajando": ("acento", "Trabajando"),
}

MAPA = '''<svg viewBox="0 0 390 160" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <path d="M-10 118 C 70 104 140 134 214 92 S 340 52 400 66" stroke="#fff" stroke-width="16" fill="none"/>
  <path d="M176 -10 L 196 70 L 222 170" stroke="#fff" stroke-width="10" fill="none"/>
  <path d="M-10 36 L 110 56 L 150 -10" stroke="#fff" stroke-width="6" fill="none"/>
  <path d="M268 -10 C 292 56 322 112 400 136" stroke="#CFE0EE" stroke-width="5" fill="none"/>
  <path d="M70 112 C 120 108 160 104 196 84" stroke="#F46B2C" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 10" fill="none"/>
</svg>'''


# ───────────────────────── Teléfonos (pantallas de la app con datos de ejemplo) ─────────────────────────

def pill(dk: Deck, ruta: str) -> str:
    estado = dk.d.crudo(ruta, defecto="asignado")
    if estado not in ESTADOS:
        dk.d.errores.append(f"«{ruta}» debe ser uno de: {', '.join(ESTADOS)}.")
        estado = "asignado"
    clase, texto = ESTADOS[estado]
    return f'<span class="pill {clase}">{texto}</span>'


def tel_tablero(dk: Deck, p: str) -> str:
    d = dk.d
    cuerpo, espera, total = [], False, 0
    for rd in d.lista(f"{p}.dias", 1, 2):
        cuerpo.append(f'<div class="ap-h">{d.t(rd + ".dia", 16)}</div>')
        for i, rt in enumerate(d.lista(f"{rd}.trabajos", 1, 3)):
            total += 1
            quien = d.crudo(rt + ".quien", 18, opcional=True)
            origen = d.crudo(rt + ".origen", defecto="propio")
            if origen not in ("propio", "fixero"):
                d.errores.append(f"«{rt}.origen» debe ser «propio» o «fixero».")
            if origen == "fixero" and d.crudo(rt + ".estado", defecto="") == "sin_asignar":
                espera = True
            avatar = (f'<span class="av">{html.escape(iniciales(quien))}</span>' if quien
                      else f'<span class="av sq">{icono("user-circle")}</span>')
            separado = ' style="margin-top:10px"' if i else ""
            cuerpo.append(
                f'<div class="ap-card"{separado}><div class="ap-row">{avatar}'
                f'<div><div class="ap-t">{d.t(rt + ".titulo", 34)}</div>'
                f'<div class="ap-m">{d.t(rt + ".hora", 16)} · {html.escape(quien) if quien else "Sin asignar"}<br>'
                f'{d.t(rt + ".comuna", 16)} · {"Cliente de Fixero" if origen == "fixero" else "Tu cliente"}</div></div>'
                f'{pill(dk, rt + ".estado")}</div></div>')
    if total > 5:
        d.avisos.append(f"«{p}» tiene {total} trabajos; con más de 5 se cortan al fondo del teléfono.")
    aviso = (f'<div class="ap-notice">{icono("bell-ringing")}<span>1 pedido de Fixero espera a alguien</span><span>Ver</span></div>'
             if espera else "")
    return (f'<div class="screen">{SB}<div class="ap"><div class="ap-nav"><span class="back">{icono("caret-left")}</span>'
            f'Tablero de trabajos</div>{aviso}{"".join(cuerpo)}</div><div class="ap-bar"></div>'
            f'<div class="ap-btn">{icono("plus")}Nuevo trabajo</div></div>')


def tel_tecnico(dk: Deck, p: str) -> str:
    d = dk.d

    def trabajos(ruta: str) -> str:
        return "".join(
            f'<div class="job"><span class="av sq gray">{icono("clipboard-text")}</span><div>'
            f'<div class="ap-t">{d.t(r + ".titulo", 34)}</div><div class="ap-m">{d.t(r + ".hora", 16)} · {d.t(r + ".direccion", 40)}</div>'
            f'{pill(dk, r + ".estado")}</div></div>'
            for r in d.lista(ruta, 1, 2))

    manana = (f'<div class="ap-h">Mañana</div><div class="ap-card">{trabajos(p + ".manana")}</div>'
              if d.hay(p + ".manana") else "")
    return (f'<div class="screen">{SB}<span class="bell">{icono("bell")}<b>1</b></span>'
            f'<div class="ap" style="padding-top:62px"><div class="ap-hello">Hola, {d.t(p + ".nombre", 14)}</div>'
            f'<div class="ap-card" style="display:grid; grid-template-columns:64px 1fr; gap:12px; padding:16px 14px; align-items:start">'
            f'<span class="co-logo" style="width:64px; height:44px; padding:4px 5px">{dk.logo_empresa("mockup")}</span>'
            f'<div><div class="ap-t">{dk.n} te asigna los trabajos</div><div class="ap-m">Aquí ves dónde y cuándo te toca cada uno. '
            f'Te avisamos cuando te asignen uno nuevo.</div></div></div>'
            f'<div class="ap-h">Hoy</div><div class="ap-card">{trabajos(p + ".hoy")}</div>{manana}</div>'
            f'<div class="tabbar"><div class="on">{icono("house")}Inicio</div><div>{icono("calendar-blank")}Agenda</div>'
            f'<div>{icono("wallet")}Ganancias</div><div>{icono("user-circle")}Perfil</div></div></div>')


def tel_cliente(dk: Deck, p: str) -> str:
    d = dk.d
    maestro = d.crudo(p + ".maestro", 18)
    insignia = d.t(p + ".insignia", 34, defecto=f"Empresa verificada · {d.crudo('empresa.nombre')}")
    return (f'<div class="screen">{SB}<div class="ap"><div class="ap-nav"><span class="back">{icono("caret-left")}</span>Tu pedido</div>'
            f'<span class="pill acento" style="margin:8px 4px 0">En camino</span>'
            f'<div style="font-size:26px; font-weight:700; letter-spacing:-.015em; margin:8px 4px 4px">'
            f'{html.escape(maestro.split()[0] if maestro else "")} llega a las {d.t(p + ".hora", 5, defecto="10:24")}</div>'
            f'<div class="ap-m" style="margin:0 4px 12px; font-size:14px">{d.t(p + ".trabajo", 40)}</div>'
            f'<div class="ap-card" style="overflow:hidden"><div class="map" style="height:150px">{MAPA}'
            f'<span class="me" style="left:58px; top:101px"></span><span class="pin" style="margin-top:-30px">{icono("house")}</span></div></div>'
            f'<div class="ap-card" style="margin-top:10px; padding:14px"><div style="display:grid; grid-template-columns:52px 1fr; gap:12px; align-items:center">'
            f'<span class="av" style="width:52px; height:52px; font-size:17px">{html.escape(iniciales(maestro))}</span>'
            f'<div><div class="ap-t" style="font-size:16.5px">{html.escape(maestro)}</div><div class="ap-m">{icono("star")} 4,9 · {d.t(p + ".oficio", 18)}</div></div></div>'
            f'<div class="badge" style="margin-top:12px">{d.icono(p + ".insignia_icono", "buildings")}<span>{insignia}</span></div>'
            f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:12px"><div class="obtn">{icono("chat-circle")}Chat</div>'
            f'<div class="obtn">{icono("phone")}Llamar</div></div></div>'
            f'<div class="code" style="margin-top:10px"><div><div class="ap-t">Código de inicio</div><div class="ap-m">Díctaselo cuando llegue.</div></div>'
            f'<div class="digits">4827</div></div>'
            f'<div style="display:flex; gap:10px; align-items:center; margin:14px 4px 0; font-size:13px; color:#5E6563">'
            f'{icono("shield-check")}Tu pago queda protegido hasta que confirmes.</div></div></div>')


def tel_perfil(dk: Deck, p: str) -> str:
    d = dk.d
    comunas = [html.escape(str(c)) for c in (d.valor("empresa.comunas") or [])]
    total = d.valor("empresa.comunas_total") or len(comunas)
    chips = "".join(f'<span class="ap-chip">{c}</span>' for c in comunas[:5])
    if isinstance(total, int) and total > min(len(comunas), 5):
        chips += f'<span class="ap-chip">+{total - min(len(comunas), 5)}</span>'
    comunas_html = (f'<div class="ap-t" style="margin:0 2px 8px">Comunas</div><div class="ap-chiprow">{chips}</div>'
                    if chips else "")
    precios = "".join(
        f'<div class="line"><div><div class="ap-t" style="font-size:14.5px">{d.t(r + ".nombre", 34)}</div>'
        f'<div class="ap-m">{d.t(r + ".detalle", 30, opcional=True)}</div></div>'
        f'<div class="ap-t" style="font-size:14.5px; white-space:nowrap">{d.t(r + ".precio", 12, defecto="Cotizar")}</div></div>'
        for r in d.lista(p + ".precios", 1, 3, opcional=True))
    precios_html = (f'<div class="ap-t" style="margin:18px 2px 8px">Precios</div><div class="ap-card" style="padding:4px 14px">{precios}</div>'
                    if precios else "")
    equipo = "".join(
        f'<div class="ap-row"><span class="av">{html.escape(iniciales(d.crudo(r + ".nombre", 18)))}</span><div>'
        f'<div class="ap-t">{d.t(r + ".nombre", 18)}</div><div class="ap-m">{icono("star")} {d.t(r + ".nota", 4, defecto="4,9")} · Verificado</div></div>'
        f'<span class="ap-m">{icono("caret-right")}</span></div>'
        for r in d.lista(p + ".equipo", 1, 2, opcional=True))
    equipo_html = (f'<div class="ap-t" style="margin:18px 2px 8px">Equipo</div><div class="ap-card team">{equipo}</div>'
                   if equipo else "")
    return (f'<div class="screen white">{SB}<div class="ap"><div class="ap-nav"><span class="back" style="background:#F2F4F3">'
            f'{icono("caret-left")}</span>Empresa</div>'
            f'<div style="display:grid; grid-template-columns:110px 1fr; gap:14px; align-items:center; margin:14px 2px 12px">'
            f'<span class="co-logo" style="width:110px; height:72px; border-radius:18px; padding:8px 10px">{dk.logo_empresa("mockup")}</span>'
            f'<div><div style="font-size:23px; font-weight:700; letter-spacing:-.015em; line-height:1.15">{dk.n}</div>'
            f'<div class="ap-m">{d.t("empresa.rubro", 26)}</div></div></div>'
            f'<div style="display:flex; gap:6px; flex-wrap:wrap"><span class="badge">{icono("buildings")}Empresa verificada</span></div>'
            f'<p class="ap-m" style="font-size:14px; margin:14px 2px 16px; color:#282B2C">{d.t("empresa.descripcion", 110)}</p>'
            f'{comunas_html}{precios_html}{equipo_html}</div>'
            f'<div class="ap-bar"></div><div class="ap-btn">{icono("file-text")}<span>Pedir cotización a {dk.n}</span></div></div>')


TELEFONOS = {
    "tablero": (tel_tablero, lambda dk: "Administrador · datos de ejemplo"),
    "tecnico": (tel_tecnico, lambda dk: f"{dk.trabajador.capitalize()} · datos de ejemplo"),
    "cliente": (tel_cliente, lambda dk: "Cliente · datos de ejemplo"),
    "perfil": (tel_perfil, lambda dk: f"Perfil de {dk.n} · datos de ejemplo"),
}


def telefono(dk: Deck, nombre: str, ruta: str) -> str:
    if nombre not in TELEFONOS:
        dk.d.errores.append(f"«{ruta}»: «{nombre}» no es un teléfono; usa {', '.join(TELEFONOS)}.")
        return ""
    if not dk.d.hay(f"telefonos.{nombre}"):
        dk.d.errores.append(f"«{ruta}» usa el teléfono «{nombre}», pero falta «telefonos.{nombre}».")
        return ""
    armar, leyenda = TELEFONOS[nombre]
    return (f'<figure class="phone-col"><div class="phone" style="--z:.96">{armar(dk, "telefonos." + nombre)}</div>'
            f'<figcaption class="note">{leyenda(dk)}</figcaption></figure>')


# ───────────────────────── Diapositivas ─────────────────────────

def s_portada(dk: Deck, fecha: str) -> str:
    d = dk.d
    return f'''
  <section class="slide dark cover is-active" aria-roledescription="diapositiva">
    <div class="cover-top">
      <div class="lockup"><div class="fx">{dk.fixero["blanco"]}</div><span class="x" aria-hidden="true">×</span><div class="sc">{dk.logo_empresa("oscuro")}</div><span class="sr">Fixero × {dk.n}</span></div>
      <span class="note">{d.t("portada.nota", 60, defecto=f"Propuesta para {d.crudo('empresa.nombre')} · {html.unescape(fecha)}")}</span>
    </div>
    <div class="cover-body">
      <div class="eyebrow"><b>Fixero × {dk.n}</b></div>
      <h1 class="display">{d.t("portada.titular", 95)}</h1>
      <p class="lead">{d.t("portada.bajada", 230)}</p>
    </div>
    <footer class="foot"><span>Santiago · fixero.cl</span><span class="pg"></span></footer>
  </section>'''


def s_punto_de_partida(dk: Deck) -> str:
    d, p = dk.d, "punto_de_partida"
    datos = d.lista(p + ".datos", 3, 4)
    hechos = "".join(f'<div class="fact"><div class="big">{d.t(r + ".cifra", 12)}</div><p class="body">{d.t(r + ".texto", 75)}</p></div>'
                     for r in datos)
    cita = d.hay(p + ".cita.texto")
    checks = "".join(f'<li>{d.icono(r + ".icono")}<span>{d.t(r + ".texto", 52 if cita else 70)}</span></li>'
                     for r in d.lista(p + ".lista", 3, 6 if not cita else 5))
    tarjeta = (f'<h3>{d.t(p + ".lista_titulo", 60)}</h3><ul class="checks{"" if cita else " dos"}">{checks}</ul>')
    if cita:
        abajo = (f'<div class="split grow"><div class="quote"><blockquote>«{d.t(p + ".cita.texto", 95)}»</blockquote>'
                 f'<p class="note">{d.t(p + ".cita.fuente", 60)}</p></div><div class="card">{tarjeta}</div></div>')
    else:
        abajo = f'<div class="card">{tarjeta}</div>'
    return f'''
  <section class="slide" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto="El punto de partida"))}
      <h2 class="title">{d.t(p + ".titulo", 95)}</h2>
    </div>
    <div class="facts" style="grid-template-columns:repeat({max(len(datos), 1)}, 1fr)">{hechos}</div>
    {abajo}
    {dk.pie()}
  </section>'''


def s_fixero(dk: Deck) -> str:
    d = dk.d
    return f'''
  <section class="slide mist" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow("Fixero en una página")}
      <h2 class="title">{d.t("fixero_titulo", 115, defecto="La app chilena para contratar maestros verificados, con el precio claro antes de empezar y el pago protegido.")}</h2>
    </div>
    <div class="modes">
      <div class="mode"><div class="icon-well">{icono("lightning")}</div><h3>Quick Fix</h3><p class="say">«Lo necesito ahora»</p><p class="body">Un maestro verificado que llega en minutos.</p></div>
      <div class="mode"><div class="icon-well">{icono("files")}</div><h3>Cotiza</h3><p class="say">«Quiero comparar»</p><p class="body">Hasta 5 ofertas en 48 horas, con fotos y video.</p></div>
      <div class="mode"><div class="icon-well">{icono("calendar-check")}</div><h3>Reserva</h3><p class="say">«Quiero a este maestro»</p><p class="body">Día y hora con el maestro que el cliente elige.</p></div>
      <div class="mode"><div class="icon-well">{icono("tag")}</div><h3>Precio fijo</h3><p class="say">«Sé lo que necesito»</p><p class="body">Trabajos con precio cerrado del catálogo.</p></div>
      <div class="mode"><div class="icon-well">{icono("arrows-clockwise")}</div><h3>Plan mensual</h3><p class="say">«Todos los meses»</p><p class="body">Mantención con el mismo maestro de siempre.</p></div>
    </div>
    <div class="pieces" style="margin-top:auto">
      <div class="piece">{icono("house")}<div><h3>Fixero</h3><p class="body">La app de los clientes, para iPhone y Android.</p></div></div>
      <div class="piece">{icono("toolbox")}<div><h3>Fixero Maestros</h3><p class="body">La app de técnicos y empresas: trabajos, agenda y pagos.</p></div></div>
      <div class="piece">{d.icono("fixero_rubro.icono", "wrench")}<div><h3>{d.t("fixero_rubro.titulo", 24, defecto=d.crudo("empresa.rubro"))}</h3><p class="body">{d.t("fixero_rubro.texto", 80)}</p></div></div>
      <div class="piece">{icono("seal-check")}<div><h3>Primeros socios</h3><p class="body">Sumamos maestros y empresas antes de abrir la app al público en Santiago.</p></div></div>
    </div>
    {dk.pie()}
  </section>'''


def s_propuesta(dk: Deck) -> str:
    d, p = dk.d, "propuesta"
    pilares = "".join(f'<div class="card pillar"><div class="icon-well">{d.icono(r + ".icono")}</div><h3>{d.t(r + ".titulo", 34)}</h3>'
                      f'<p class="body">{d.t(r + ".texto", 210)}</p></div>' for r in d.lista(p + ".pilares", 3, 3))
    return f'''
  <section class="slide dark" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto="La propuesta"))}
      <h2 class="title">{d.t(p + ".titulo", 100)}</h2>
    </div>
    <p class="lead" style="max-width:1300px">{d.t(p + ".bajada", 190)}</p>
    <div class="pillars">{pilares}</div>
    {dk.pie()}
  </section>'''


def s_con_telefonos(dk: Deck, p: str, clase: str, eyebrow: str, telefonos: list[tuple[str, str]], filas: str) -> str:
    d = dk.d
    n = filas.count('class="row"')
    estilo = f"grid-template-columns:1fr; gap:{26 if n > 4 else 40 if n == 4 else 56}px"
    if len(telefonos) == 1:
        estilo += "; max-width:1040px"
    return f'''
  <section class="slide {clase}" aria-roledescription="diapositiva">
    <div class="with-phones">
      <div class="text">
        <div class="head">
          {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto=eyebrow))}
          <h2 class="title">{d.t(p + ".titulo", 50 if len(telefonos) == 2 else 80)}</h2>
        </div>
        <ol class="rows" style="{estilo}">{filas}</ol>
      </div>
      <div class="phones">{"".join(telefono(dk, n, r) for n, r in telefonos)}</div>
    </div>
    {dk.pie()}
  </section>'''


def s_como_funciona(dk: Deck) -> str:
    d, p = dk.d, "como_funciona"
    tels = d.valor(p + ".telefonos") or []
    if not isinstance(tels, list) or not 1 <= len(tels) <= 2:
        d.errores.append(f"«{p}.telefonos» debe ser una lista de 1 o 2 teléfonos ({', '.join(TELEFONOS)}).")
        tels = tels[:2] if isinstance(tels, list) else []
    filas = dk.filas(p + ".pasos", 3, 5, 42, 100 if len(tels) == 2 else 150)
    return s_con_telefonos(dk, p, "mist", "Cómo funcionaría", [(n, f"{p}.telefonos[{i}]") for i, n in enumerate(tels)], filas)


def s_beneficios(dk: Deck) -> str:
    d, p = dk.d, "beneficios"
    items = d.lista(p + ".items", 6, 8)
    columnas = 4 if len(items) == 8 else 3
    tiles = "".join(f'<div class="tile"><div class="t">{d.icono(r + ".icono")}<h3>{d.t(r + ".titulo", 30)}</h3></div>'
                    f'<p class="body">{d.t(r + ".texto", 115 if columnas == 4 else 150)}</p></div>' for r in items)
    if len(items) == 7:
        d.errores.append(f"«{p}.items» debe tener 6 u 8 beneficios (7 deja un hueco).")
    return f'''
  <section class="slide" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto=f"Beneficios para {d.crudo('empresa.nombre')}"))}
      <h2 class="title">{d.t(p + ".titulo", 70)}</h2>
    </div>
    <div class="grid g{columnas} grow" style="grid-auto-rows:1fr">{tiles}</div>
    {dk.pie()}
  </section>'''


def s_marca(dk: Deck) -> str:
    d, p = dk.d, "marca"
    nombre = d.crudo(p + ".telefono", defecto="perfil")
    filas = dk.filas(p + ".puntos", 3, 4, 42, 160)
    return s_con_telefonos(dk, p, "mist", f"{d.crudo('empresa.nombre')} en Fixero", [(nombre, p + ".telefono")], filas)


def s_antes_despues(dk: Deck) -> str:
    d, p = dk.d, "antes_despues"
    filas = "".join(
        f'<div class="k" role="rowheader">{d.t(r + ".tema", 16)}</div><div class="a" role="cell">{d.t(r + ".hoy", 52)}</div>'
        f'<div class="b" role="cell">{icono("check")}{d.t(r + ".con_fixero", 54)}</div>'
        for r in d.lista(p + ".filas", 4, 8))
    return f'''
  <section class="slide" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto="Lo que cambia"))}
      <h2 class="title">{d.t(p + ".titulo", 80)}</h2>
    </div>
    <div class="compare" role="table" aria-label="{d.t(p + ".col_hoy", defecto="Coordinación manual", attr=True)} comparado con Fixero">
      <div class="h k" role="columnheader"></div>
      <div class="h a" role="columnheader">{d.t(p + ".col_hoy", 28, defecto="Coordinación manual")}</div>
      <div class="h b" role="columnheader">Con Fixero</div>
      {filas}
    </div>
    {dk.pie()}
  </section>'''


SEGURIDAD = {
    "personas": ("identification-card", "Cada persona, verificada", "Cédula por ambos lados, selfie con cámara guiada y antecedentes, revisados por el equipo de Fixero."),
    "empresa": ("buildings", "La empresa, verificada", "RUT, e-RUT, inicio de actividades y una cuenta bancaria a nombre de la empresa."),
    "codigo": ("key", "Código de inicio", "El trabajo empieza cuando el cliente dicta su código de 4 dígitos, con comprobación de GPS."),
    "apertura": ("door-open", "Apertura de puertas", "No se abre una vivienda sin revisar la cédula y un respaldo de que la persona vive ahí."),
    "sec": ("lightning", "Licencia SEC", "Gásfiter y electricistas suben su licencia, y Fixero la comprueba en el validador público de la SEC."),
    "pago": ("shield-check", "Pago protegido", "El cliente paga con tarjeta al pedir, y el dinero se libera cuando confirma que todo quedó bien."),
    "garantia": ("seal-check", "Garantía de 30 días", "Si algo falla, el mismo maestro vuelve sin costo o Fixero manda a otro."),
    "fotos": ("camera", "Respaldo de cada trabajo", "Fotos de antes y después, y un comprobante en PDF con el detalle."),
    "reclamos": ("scales", "Reclamos con mediación", "48 horas para acordar en el chat; después decide Fixero, con derecho a apelación."),
    "dinero": ("lock-key", "Dinero con registro", "Cada peso queda en un libro contable de doble entrada, y un cobro nunca se duplica."),
}


def s_seguridad(dk: Deck) -> str:
    d, p = dk.d, "seguridad"
    claves = d.valor(p + ".tarjetas") or ["personas", "empresa", "codigo", "pago", "reclamos", "garantia"]
    tarjetas = []
    for i, c in enumerate(claves[:6]):
        if isinstance(c, dict):
            r = f"{p}.tarjetas[{i}]"
            ic, ti, te = d.icono(r + ".icono"), d.t(r + ".titulo", 34), d.t(r + ".texto", 120)
        elif c in SEGURIDAD:
            nombre_ic, ti, te = SEGURIDAD[c]
            ic = icono(nombre_ic)
        else:
            d.errores.append(f"«{p}.tarjetas[{i}]»: «{c}» no existe; usa {', '.join(SEGURIDAD)} o un objeto con icono, titulo y texto.")
            continue
        tarjetas.append(f'<div class="card"><div class="icon-well">{ic}</div><h3>{ti}</h3><p class="body">{te}</p></div>')
    if len(claves) != 6:
        d.errores.append(f"«{p}.tarjetas» debe tener 6 tarjetas.")
    return f'''
  <section class="slide dark" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow("Seguridad y confianza")}
      <h2 class="title">{d.t(p + ".titulo", 85, defecto="Quien entra a una casa por Fixero está verificado.")}</h2>
    </div>
    <div class="grid g3 grow" style="grid-auto-rows:1fr">{"".join(tarjetas)}</div>
    {dk.pie()}
  </section>'''


def s_alianza(dk: Deck) -> str:
    d, p = dk.d, "alianza"
    opciones = d.lista(p + ".opciones", 3, 5)
    tarjetas = []
    for i, r in enumerate(opciones):
        etiqueta = d.t(r + ".etiqueta", 24, opcional=True)
        rec = " rec" if d.valor(r + ".recomendada") else ""
        chip = f'<span class="chip">{etiqueta}</span>' if etiqueta else ""
        tarjetas.append(f'<div class="opt{rec}"><div class="top"><span class="letter">{"ABCDE"[i]}</span>{chip}</div>'
                        f'<h3>{d.t(r + ".titulo", 34)}</h3><p class="body">{d.t(r + ".texto", 150)}</p></div>')
    nota = d.t(p + ".nota", 110, opcional=True)
    return f'''
  <section class="slide mist" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto="Cómo trabajar juntos"))}
      <h2 class="title">{d.t(p + ".titulo", 100)}</h2>
    </div>
    <div class="ladder" style="grid-template-columns:repeat({max(len(opciones), 1)}, 1fr)">{"".join(tarjetas)}</div>
    {f'<p class="note ladder-note">{nota}</p>' if nota else ""}
    {dk.pie()}
  </section>'''


def s_reunion(dk: Deck) -> str:
    d, p = dk.d, "reunion"
    pasos = "".join(f'<li class="step"><div class="num">{i + 1:02d}</div><h3>{d.t(r + ".titulo", 40)}</h3>'
                    f'<p class="body">{d.t(r + ".texto", 125)}</p></li>' for i, r in enumerate(d.lista(p + ".mostraremos", 3, 4)))
    ideas = "".join(f'<li>{d.icono(r + ".icono")}<span><strong>{d.t(r + ".titulo", 40)}.</strong> {d.t(r + ".texto", 85)}</span></li>'
                    for r in d.lista(p + ".ideas", 2, 4))
    return f'''
  <section class="slide" aria-roledescription="diapositiva">
    <div class="head">
      {dk.eyebrow(d.t(p + ".eyebrow", 40, defecto="La reunión"))}
      <h2 class="title">{d.t(p + ".titulo", 95)}</h2>
    </div>
    <div class="pilot grow">
      <ol class="timeline">{pasos}</ol>
      <div class="needs">
        <h3>{d.t(p + ".ideas_titulo", 34, defecto="Ideas para conversar")}</h3>
        <p class="note">Por acordar juntos</p>
        <ul>{ideas}</ul>
      </div>
    </div>
    {dk.pie()}
  </section>'''


def s_cierre(dk: Deck, remitente: dict) -> str:
    d = dk.d
    nombre = html.escape(remitente["nombre"])
    telefono_txt = remitente.get("telefono", "")
    correo = remitente.get("correo", "")
    asunto = urllib.parse.quote(f"Reunión Fixero × {d.crudo('empresa.nombre')}")
    if remitente.get("agenda_url"):
        url, etiqueta = remitente["agenda_url"], "Agendar la reunión"
    elif telefono_txt:
        mensaje = (f"Hola {remitente['nombre'].split()[0]}, vi la presentación de Fixero para "
                   f"{d.crudo('empresa.nombre')} y me gustaría agendar una reunión.")
        url = f"https://wa.me/{re.sub(r'[^0-9]', '', telefono_txt)}?text={urllib.parse.quote(mensaje)}"
        etiqueta = "Agendar por WhatsApp"
    else:
        url, etiqueta = f"mailto:{correo}?subject={asunto}", "Agendar por correo"
    contacto = [f'<div class="name">{nombre}</div>', f'<div>{html.escape(remitente.get("cargo", ""))}</div>']
    if telefono_txt:
        contacto.append(f'<div class="tel">{html.escape(telefono_txt)}</div>')
    linea = " · ".join(x for x in [f'<a href="mailto:{html.escape(correo)}?subject={asunto}">{html.escape(correo)}</a>' if correo else "",
                                    '<a href="https://fixero.cl">fixero.cl</a>'] if x)
    contacto.append(f"<div>{linea}</div>")
    return f'''
  <section class="slide orange closing" aria-roledescription="diapositiva">
    <div class="top"><div class="lockup"><div class="fx">{dk.fixero["grafito"]}</div><span class="x" aria-hidden="true">×</span><div class="sc">{dk.logo_empresa("naranja")}</div><span class="sr">Fixero × {dk.n}</span></div></div>
    <div>
      <h2 class="display">{d.t("cierre.titular", 40, defecto="Agendemos 30 minutos.")}</h2>
      <p class="lead">{d.t("cierre.bajada", 160)}</p>
      <a class="cta" href="{html.escape(url)}">{icono("calendar-check")}{etiqueta}</a>
    </div>
    <div class="closing-bottom">
      <div></div>
      <div class="contact">{"".join(contacto)}</div>
    </div>
    <footer class="foot"><span>Fixero × {dk.n}</span><span class="pg"></span></footer>
  </section>'''


# ───────────────────────── Armado ─────────────────────────

def armar(ruta_json: Path, salida: Path) -> tuple[Path | None, Datos]:
    raiz = json.loads(ruta_json.read_text(encoding="utf-8"))
    d = Datos(raiz)
    dk = Deck(d, ruta_json.parent)

    hoy = datetime.date.today()
    fecha = d.t("fecha", 20, defecto=f"{MESES[hoy.month - 1]} {hoy.year}")
    remitentes = json.loads((SKILL / "remitentes.json").read_text(encoding="utf-8"))
    rem = d.valor("remitente") or "benjamin"
    if isinstance(rem, str):
        if rem.lower() not in remitentes:
            d.errores.append(f"«remitente»: «{rem}» no está en remitentes.json ({', '.join(remitentes)}).")
            rem = remitentes["benjamin"]
        else:
            rem = remitentes[rem.lower()]

    # punto_de_partida, propuesta y reunion se pueden omitir en un deck que solo presenta a Fixero, sin propuesta.
    diapositivas = [s_portada(dk, fecha)]
    if d.hay("punto_de_partida"):
        diapositivas.append(s_punto_de_partida(dk))
    diapositivas.append(s_fixero(dk))
    if d.hay("propuesta"):
        diapositivas.append(s_propuesta(dk))
    diapositivas += [s_como_funciona(dk), s_beneficios(dk)]
    if d.hay("marca"):
        diapositivas.append(s_marca(dk))
    if d.hay("antes_despues"):
        diapositivas.append(s_antes_despues(dk))
    diapositivas.append(s_seguridad(dk))
    if d.hay("alianza"):
        diapositivas.append(s_alianza(dk))
    if d.hay("reunion"):
        diapositivas.append(s_reunion(dk))
    diapositivas.append(s_cierre(dk, rem))

    portada = d.crudo("portada.imagen", opcional=True)
    estilo_portada = ""
    if portada == "ninguna":
        estilo_portada = ('.cover::before{background:radial-gradient(circle at 80% 28%,rgba(244,107,44,.30),rgba(244,107,44,0) 52%),'
                          'radial-gradient(circle at 12% 90%,rgba(244,107,44,.10),rgba(244,107,44,0) 40%),var(--noche)}'
                          '.cover::after{display:none}')
    elif portada:
        foto = (ruta_json.parent / portada).resolve()
        try:
            estilo_portada = f'.cover::before{{background-image:url("{data_uri(foto)}")}}'
        except (OSError, ValueError) as e:
            d.errores.append(f"«portada.imagen»: {e}")
    if not d.hay("fuentes"):
        d.errores.append("Falta «fuentes»: anota de dónde salió cada dato de la empresa ({dato, url}).")
    if d.errores:
        return None, d

    css = (PLANTILLA / "deck.css").read_text()
    css = css.replace("{{font:public-sans}}", data_uri(ASSETS / "fuentes/public-sans.woff2"))
    css = css.replace("{{font:manrope}}", data_uri(ASSETS / "fuentes/manrope.ttf"))
    css = css.replace("{{img:poster}}", data_uri(ASSETS / "portada.jpg"))
    js = (PLANTILLA / "deck.js").read_text()
    total = len(diapositivas)
    n = dk.n_attr
    documento = f'''<!doctype html>
<html lang="es-CL" class="mode-deck no-anim">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fixero × {n}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{d.t('portada.bajada', attr=True)}">
<style>
{css}
{estilo_portada}
</style>
</head>
<body>
<div class="progress" aria-hidden="true"></div>

<main class="deck" id="deck" aria-roledescription="presentación" aria-label="Fixero × {n}">
{"".join(diapositivas)}

</main>

<nav class="nav" aria-label="Navegación de la presentación">
  <button type="button" data-go="prev" aria-label="Anterior">{icono("caret-left")}</button>
  <span class="count" aria-live="polite">01 / {total:02d}</span>
  <button type="button" data-go="next" aria-label="Siguiente">{icono("caret-right")}</button>
  <button type="button" data-go="full" aria-label="Pantalla completa">{icono("corners-out")}</button>
</nav>
<div class="hint" aria-hidden="true">← → para avanzar · F pantalla completa</div>

<script>
{js}
</script>
</body>
</html>
'''
    visible = re.sub(r"data:[^\"')]+", "", documento).lower()
    if "scanavini" not in dk.n_attr.lower() and "scanavini" in visible:
        d.errores.append("Quedó texto del ejemplo (el deck dice «Scanavini»): reescribe todos los textos para esta empresa.")
        return None, d
    salida.mkdir(parents=True, exist_ok=True)
    archivo = salida / f"Fixero-{slug(d.crudo('empresa.nombre'))}.html"
    archivo.write_text(documento, encoding="utf-8")
    escribir_fuentes(d, salida, fecha)
    return archivo, d


def escribir_fuentes(d: Datos, salida: Path, fecha: str) -> None:
    lineas = [f"# Fuentes · Fixero × {d.crudo('empresa.nombre')}", "",
              f"Fecha del deck: {fecha}. Web: {d.crudo('empresa.web', opcional=True) or '—'}. "
              f"Ángulo: {d.crudo('angulo', opcional=True) or '—'}.", "", "## De dónde sale cada dato", ""]
    for r in d.lista("fuentes", 1, 40):
        lineas.append(f"- {d.crudo(r + '.dato')}: {d.crudo(r + '.url')}")
    pendientes = d.valor("por_confirmar") or []
    if pendientes:
        lineas += ["", "## Por confirmar antes de enviar", ""] + [f"- {p}" for p in pendientes]
    if d.hay("empresa.logo"):
        lineas += ["", "## Logo", "", f"- {d.crudo('empresa.logo')} · {d.crudo('empresa.logo_fuente', opcional=True) or 'origen sin anotar'}"]
    (salida / "fuentes.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def revisar(chrome: str, html_path: Path, total: int) -> tuple[list[int] | None, list[Path]]:
    url = html_path.resolve().as_uri() + "?revisar"
    malas = None
    for _ in range(4):  # Chrome a veces entrega la página antes de que termine de medir: se reintenta
        dom = navegador.dom(chrome, url)
        m = re.search(r'data-desbordes="([^"]*)"', dom)
        if m and 'data-revisado="si"' in dom:
            malas = [int(x) for x in m.group(1).split(",") if x]
            break
    carpeta = html_path.parent / "revision"
    carpeta.mkdir(exist_ok=True)
    for viejo in carpeta.glob("*.png"):
        viejo.unlink()

    def una(i: int) -> Path | None:
        png = carpeta / f"{i:02d}.png"
        return png if navegador.captura(chrome, f"{url}#{i}", png) else None

    with ThreadPoolExecutor(max_workers=4) as pool:
        capturas = [p for p in pool.map(una, range(1, total + 1)) if p]

    # Hoja de contactos: todo el deck en una imagen, para revisarlo de un vistazo.
    if capturas:
        filas = -(-len(capturas) // 3)
        miniaturas = "".join(f'<figure><img src="{p.name}"><figcaption>{p.stem}</figcaption></figure>' for p in capturas)
        hoja = carpeta / "hoja.html"
        hoja.write_text(
            '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#2A2D2E;font:600 18px ui-monospace,Menlo,monospace;color:#ccc}'
            'main{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:24px}figure{margin:0}'
            'img{display:block;width:100%;border-radius:6px}figcaption{margin-top:6px}</style>'
            f'<main>{miniaturas}</main>', encoding="utf-8")
        navegador.captura(chrome, hoja.resolve().as_uri(), carpeta / "hoja.png", 1920, 24 + filas * (346 + 24 + 34))
        hoja.unlink()
    return malas, capturas


def main() -> None:
    ap = argparse.ArgumentParser(description="Arma la presentación de Fixero para una empresa.")
    ap.add_argument("empresa", help="empresa.json o la carpeta que lo contiene")
    ap.add_argument("--pdf", action="store_true", help="también el PDF (necesita Chrome, Chromium, Edge o Brave)")
    ap.add_argument("--revisar", action="store_true", help="capturas por diapositiva y revisión de desbordes")
    ap.add_argument("--salida", help="carpeta de salida (por defecto, la del JSON)")
    args = ap.parse_args()

    ruta = Path(args.empresa).expanduser()
    if ruta.is_dir():
        ruta = ruta / "empresa.json"
    if not ruta.exists():
        sys.exit(f"No encuentro {ruta}")
    salida = Path(args.salida).expanduser() if args.salida else ruta.parent

    try:
        archivo, d = armar(ruta, salida)
    except json.JSONDecodeError as e:
        sys.exit(f"{ruta.name} no es un JSON válido: {e}")
    for a in d.avisos:
        print(f"AVISO  {a}")
    if archivo is None:
        for e in d.errores:
            print(f"ERROR  {e}")
        sys.exit(1)
    total = archivo.read_text(encoding="utf-8").count('aria-roledescription="diapositiva"')
    print(f"HTML   {archivo} · {total} diapositivas · {archivo.stat().st_size // 1024} KB")

    falla = False
    if args.pdf or args.revisar:
        chrome = navegador.encontrar()
        if not chrome:
            print("SIN CHROME  No encontré Chrome/Chromium/Edge/Brave (o la variable CHROME). El HTML está listo: "
                  "ábrelo, Cmd/Ctrl+P → Guardar como PDF, márgenes «Ninguno» y «Gráficos de fondo» activado.")
        else:
            if args.revisar:
                malas, capturas = revisar(chrome, archivo, total)
                print(f"CAPTURAS {len(capturas)} en {archivo.parent / 'revision'} (todo el deck en revision/hoja.png)")
                if malas is None:
                    print("REVISIÓN  No se pudo medir los desbordes (4 intentos); vuelve a correr o mira las capturas una por una.")
                elif malas:
                    falla = True
                    print(f"DESBORDE  Diapositivas {', '.join(map(str, malas))}: el texto se sale de su espacio "
                          "(marcado en rojo en las capturas). Acorta ese texto y vuelve a armar.")
                else:
                    print("REVISIÓN  Nada se sale de su espacio.")
            if args.pdf:
                pdf = archivo.with_suffix(".pdf")
                print(f"PDF    {pdf}" if navegador.pdf(chrome, archivo, pdf) else "PDF    No se pudo generar el PDF.")
    print(f"FUENTES {archivo.parent / 'fuentes.md'}")
    sys.exit(1 if falla else 0)


if __name__ == "__main__":
    main()
