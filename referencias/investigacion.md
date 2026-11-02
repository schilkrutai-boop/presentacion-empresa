# Cómo investigar a la empresa

La presentación convence si la empresa se reconoce en la diapositiva 2: datos concretos de ellos, no frases que sirven para cualquiera. Dedica a esto el tiempo que haga falta.

## Dónde buscar

Usa las herramientas web que tengas (búsqueda web y lectura de páginas, o el navegador integrado). Abre cada fuente: no escribas nada a partir del resumen de un buscador.

1. **Su sitio oficial**: inicio, «Nosotros» o «Quiénes somos», servicios, cobertura, preguntas frecuentes, tienda, términos y condiciones, blog. Los términos y las preguntas frecuentes suelen decir cómo agendan, cómo cobran y quién instala.
2. **Su tienda online** si vende productos: fichas de instalación, precios de servicios, despacho y cobertura.
3. **Google Maps / perfil de Google**: dirección, comuna, nota y cantidad de reseñas (si la usas, anota la fecha).
4. **Redes**: Instagram, Facebook o LinkedIn para tamaño del equipo, años, fotos del equipo con uniforme, cómo agendan («escríbenos al WhatsApp»).
5. **Ofertas de empleo** (LinkedIn, Laborum, Computrabajo): si contratan técnicos, instaladores u operarios, tienen equipo propio. Antes de atribuirles un aviso, confirma que es la misma empresa (razón social o sitio): hay muchos nombres parecidos.
6. **Prensa o directorios** solo si aportan un dato verificable (años, premios, número de clientes que ellos mismos publican).
7. **Listas de Fixero**: si la persona trabaja en el computador de Fixero, mira si la empresa ya está en `empresas-tipo-scanavini.csv` o `contactos-empresas-tipo-scanavini.csv` (columnas «Qué vende», «Tipo», «Por qué calza», y «Notas» si existe: a veces avisa que el sitio responde solo sin «www.» o algo parecido). Úsalo como pista y compruébalo en la fuente. Esas listas son internas: en `fuentes` cita la página de la empresa, no la lista.

## Qué anotar

- Qué venden o qué servicios prestan, con nombres concretos (y precios si los publican).
- Desde cuándo existen (años), tamaño (técnicos, sucursales, clientes que ellos declaran).
- Dónde atienden: comunas o regiones. Para el perfil del teléfono, hasta 5 comunas y el total.
- Cómo funciona hoy su servicio: cómo se agenda (WhatsApp, formulario, teléfono, «te contactamos»), quién va (equipo propio, técnicos independientes, una lista de terceros), cómo se paga, qué garantía dan.
- Una frase textual de su sitio que muestre el punto de partida (máximo ~15 palabras, con la página de donde sale). Por ejemplo: «Luego de recibir el producto, agendaremos tu instalación.»
- Lo que los hace distintos (garantía de por vida, certificaciones, sello SEC, 24/7…).
- Tipo de empresa para elegir el ángulo (referencias/angulos.md).

Cada dato que uses va en `"fuentes"` con la URL exacta de la página donde lo leíste (no solo el dominio). Si un número solo aparece en su propio sitio y no pudiste comprobarlo en otra parte (la nota de Google, la cantidad de clientes), úsalo como «según su sitio» y anótalo en `"por_confirmar"`. Lo dudoso (un dato de un directorio viejo, un número que no se repite en su sitio) va en `"por_confirmar"` o no va.

## Cuidado

- **No inventes.** Si no encontraste cuántos técnicos tienen, no pongas un número: usa otro dato (años, comunas, servicios).
- **No los critiques.** «Agenda solo por WhatsApp» es un dato; «su agenda es un caos» es una opinión que cierra puertas. Describe el punto de partida como oportunidad.
- **No uses sus fotos** ni textos largos de su sitio: solo el logo y una cita corta.
- **No los contactes**: la skill solo investiga y arma el archivo.
- Si el sitio no carga o la empresa casi no tiene presencia web, dilo en el resumen final y arma un deck más genérico solo si la persona lo pide.

## El logo

1. Corre `python3 <skill>/scripts/buscar_logo.py <sitio> --carpeta <carpeta de la empresa>`. Descarga los candidatos a `logo-candidatos/` y arma `candidatos.png` con cada uno sobre fondo blanco y oscuro.
2. Mira `candidatos.png`. Elige, en este orden: SVG oficial con el nombre (logotipo completo, no solo el símbolo) → PNG o WebP con fondo transparente de al menos 300 px de ancho → el ícono, solo si no hay otra cosa. Descarta los marcados «de otro sitio» (suelen ser logos de Google, Webpay o redes) y og:image (casi siempre es una foto).
3. Copia el elegido a la carpeta de la empresa como `logo.<ext>` y anota de dónde salió en `"logo_fuente"`.
4. ¿Cómo se ve sobre la portada oscura?
   - Si tienen una versión clara (blanca) del logo, guárdala como `logo-claro.<ext>` y ponla en `"logo_claro"`.
   - Si el logo es de un solo color, `"logo_en_oscuro": "blanco"` lo pinta blanco.
   - Si tiene varios colores o fondo propio, deja `"chip"` (va sobre una placa blanca redondeada).
   - Si el único logotipo viene con fondo blanco (JPG, WebP o PNG sin transparencia), usa `"chip"` en la portada y en el cierre: `"blanco"` lo convertiría en un rectángulo blanco.
   - En el cierre naranjo, `"logo_en_naranja": "directo"` solo si se lee bien sobre naranjo; si no, `"chip"`.
5. Si el sitio bloquea la descarga, busca el logo con el navegador (en su sitio, Instagram o LinkedIn), copia la dirección de la imagen y pásala directo: `buscar_logo.py https://…/logo.svg --carpeta … --sumar` (`--sumar` conserva los candidatos que ya tenías). El script ya prueba el dominio con y sin «www.».
6. Sin logo usable, no pongas `"logo"`: el deck usa el nombre de la empresa escrito como logotipo. Dilo en el resumen final.
