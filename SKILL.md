---
name: presentacion-empresa
description: Arma la presentación de Fixero para una empresa, o una por empresa para una lista, con el diseño del deck Fixero × Scanavini. Investiga en internet qué hace la empresa, busca su logo, elige qué ofrecerle (equipo propio, Fixero instala o mixto) y entrega un HTML autocontenido y un PDF cuyo objetivo es conseguir una reunión para mostrarles cómo funcionaría Fixero con su empresa. Úsala cuando pidan una presentación, deck o propuesta para una empresa ("hazle una presentación a X", "deck para estas empresas", "presentaciones para las empresas tipo Scanavini"), o pasen el nombre, la web o un CSV de empresas a las que Fixero quiere contactar.
argument-hint: "<empresa o web> [, otra…] | <archivo.csv> [filtro] [firma: benjamin|nicol]"
---

# Presentación de Fixero para una empresa

Por cada empresa produces un deck de 9 a 12 diapositivas (según las secciones opcionales) con el diseño del deck Fixero × Scanavini: quiénes son (investigado), qué es Fixero, qué les ofrecemos, cómo funcionaría con sus propios servicios en las pantallas de la app, y un cierre cuyo único objetivo es agendar una reunión de 30 minutos para mostrarles Fixero en vivo. Por empresa quedan `Fixero-<Empresa>.html` (un solo archivo, sin dependencias), `Fixero-<Empresa>.pdf` y `fuentes.md`.

`<skill>` es la carpeta de esta skill (aparece al cargarla). Todo lo que lee la persona, el deck y tus resúmenes, va en español de Chile.

## 0. Entender el pedido

- **Empresas:** nombres, sitios web o un CSV (por ejemplo `empresas-tipo-scanavini.csv`, con un filtro: un rubro, números de fila). Si son varias, sigue también «Varias empresas».
- **Quién firma:** el cierre muestra su contacto y un botón «Agendar por WhatsApp» hacia esa persona. `"remitente": "benjamin"` (por defecto) o `"nicol"`; los datos están en `<skill>/remitentes.json`. Si quien pide dice quién es, usa esa persona.
- **Dónde:** `presentaciones/<Empresa>/` dentro de la carpeta de trabajo, salvo que pidan otra. Si el entorno tiene una carpeta de salida para la persona (como en claude.ai), ahí.
- Pregunta solo si no sabes de qué empresa se trata. Lo demás tiene valor por defecto.

## 1. Investigar la empresa

Sigue `<skill>/referencias/investigacion.md`. Abre cada fuente; cada dato que uses va en `"fuentes"` con su URL exacta. Nunca inventes una cifra, un tamaño de equipo ni una cita.

## 2. Elegir el ángulo

Lee `<skill>/referencias/angulos.md` y elige A (equipo propio), B (vende, Fixero instala), C (mixto) o D (plataforma, posible competidor). **Con D, detente en esa empresa** y avisa, salvo que te confirmen que igual la hagas.

## 3. Conseguir el logo

```bash
python3 <skill>/scripts/buscar_logo.py <su sitio> --carpeta <carpeta de la empresa>
```

Si el sitio no deja leer el logo, pasa la dirección de la imagen directo (con `--sumar` para no borrar los candidatos). Mira `logo-candidatos/candidatos.png`, copia el mejor como `<carpeta de la empresa>/logo.<ext>` y decide cómo va sobre fondo oscuro y naranjo (investigacion.md, «El logo»).

## 4. Escribir `empresa.json`

Parte de una copia de `<skill>/referencias/empresa.ejemplo.json` (Scanavini, ángulo C, con todos los campos) y reescribe **todos** los textos para esta empresa. Antes de escribir, lee:
- `<skill>/referencias/fixero.md`: lo que se puede decir de Fixero. Lo no construido va solo en `reunion.ideas`. Nada de precios, comisiones, cifras de uso ni nombres de otras empresas que conversan con Fixero.
- `<skill>/referencias/escritura.md`: la voz, qué debe lograr cada diapositiva y los datos de ejemplo de los teléfonos.
- `<skill>/referencias/campos.md`: cada campo del JSON, cuáles son opcionales, sus valores por defecto y sus largos.

Secciones opcionales: quita `"marca"` o `"antes_despues"` cuando no calcen (el ángulo B normalmente no lleva `"marca"`). Para una alianza más grande que sumarse como empresa (llevar Fixero a otro país, una sociedad), agrega `"alianza"`: una diapositiva antes de la reunión con 3 a 5 formas de trabajar juntos, sin condiciones (campos.md). Lo que quien firma debe revisar antes de enviar (un dato de un directorio viejo, una categoría que Fixero no tiene) va en `"por_confirmar"`.

## 5. Armar y revisar

```bash
python3 <skill>/scripts/armar.py <carpeta de la empresa> --pdf --revisar
```

- `ERROR`: corrige el JSON y vuelve a correr. «No se pudo medir los desbordes» (después de 4 intentos): vuelve a correr. `AVISO`: un texto pasa el largo sugerido; acórtalo, salvo que la revisión muestre que cabe.
- `DESBORDE`: en esas diapositivas el texto se sale de su espacio o queda tapado dentro de un teléfono (marcado en rojo en las capturas). Acórtalo y repite hasta que diga «Nada se sale de su espacio».
- Mira `revision/hoja.png` (todo el deck en una imagen) y abre `revision/NN.png` de lo que se vea raro: que el logo se lea en la portada oscura y en el cierre naranjo, cómo cortan los títulos, los teléfonos. Corrige y vuelve a armar. No entregues un deck que no miraste.

Sin Chrome (ni Chromium, Edge o Brave, ni la variable `CHROME` con su ruta), el script igual escribe el HTML: avisa que el PDF se saca abriendo el HTML e imprimiendo como PDF, con márgenes «Ninguno» y «Gráficos de fondo» activado.

## 6. Entregar

Por empresa, cuéntale a la persona: dónde están el PDF y el HTML, el ángulo en una línea, los 2 o 3 datos en que se apoya el deck, de dónde salió el logo y cada punto de `por_confirmar`. El HTML funciona solo: se manda por correo o se abre para presentar (flechas para avanzar, F para pantalla completa; en un celular se vuelve una página con scroll). Nunca envíes, publiques ni subas el deck: lo envía quien firma.

## Varias empresas

1. Arma la lista (del pedido o del CSV con su filtro). Si son más de 10, di cuántas son en una línea antes de partir.
2. Haz la primera empresa tú, de principio a fin: fija la estructura de carpetas y muestra los problemas temprano.
3. Para el resto, si puedes lanzar subagentes, dale a cada uno una empresa (hasta 5 a la vez) con este encargo: la ruta de la skill, el nombre y el sitio de la empresa, su carpeta, quién firma, las notas de su fila del CSV y «Sigue los pasos 1 a 5 de <skill>/SKILL.md para esta empresa y responde con: la carpeta, el ángulo, los datos usados, de dónde salió el logo, por_confirmar y la última línea de la revisión de `armar.py` (debe decir «Nada se sale de su espacio»)». Sin subagentes, una por una.
4. Revisa cada resultado tú: abre su `revision/hoja.png` y vuelve a correr `armar.py --revisar` en las que fallaron.
5. Termina con una tabla: empresa, ángulo, ruta del PDF, logo sí o no, puntos por confirmar.

## Mantener la skill al día

- Otra persona que firma o un enlace para agendar: edita `<skill>/remitentes.json` (`agenda_url` cambia el botón de WhatsApp por «Agendar la reunión»).
- Cuando Fixero lance algo o un precio se haga público: actualiza `<skill>/referencias/fixero.md` y, si cambia una diapositiva fija (la 3 o la 9), sus textos en `scripts/armar.py`.
- El diseño (CSS y navegación) está en `<skill>/plantilla/`; el HTML de cada diapositiva, en `scripts/armar.py`.
