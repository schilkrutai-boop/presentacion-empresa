# Campos de empresa.json

Todos los campos que lee `scripts/armar.py`. El ejemplo completo es `empresa.ejemplo.json` (ángulo C). «Largo» es el máximo sugerido en caracteres: pasarlo da un `AVISO`; lo que manda es la revisión (`--revisar`), que marca lo que de verdad se sale.

El nombre de la empresa nunca se corta entre dos líneas: `armar.py` lo mantiene junto en todos los textos. Si un título con el nombre queda feo, acórtalo.

## Empresa y entrega

| Campo | Obligatorio | Largo | Qué es |
|---|---|---|---|
| `empresa.nombre` | sí | 40 | Nombre corto, como lo usan ellos («Clean & Go», no la razón social). |
| `empresa.web` | no | | Su sitio (va a fuentes.md). |
| `empresa.rubro` | sí | 26 | Su oficio en palabras de cliente («Aseo de hogares», «Cerrajería»). |
| `empresa.trabajador` | no | 20 | Cómo llaman a su gente, en singular: «técnico» (por defecto), «instalador», «operaria», «supervisora». Sale en la leyenda del teléfono del técnico. |
| `empresa.descripcion` | si hay teléfono `perfil` | 110 | La bio de su perfil en Fixero, en primera persona plural. |
| `empresa.comunas` | no | | Hasta 5 comunas para el perfil. |
| `empresa.comunas_total` | no | | Total de comunas; muestra «+N». |
| `empresa.logo` | no | | Archivo del logo en la carpeta de la empresa. Sin logo, el deck escribe el nombre. |
| `empresa.logo_claro` | no | | Versión clara para la portada oscura. |
| `empresa.logo_fuente` | no | | De dónde salió el logo (va a fuentes.md). |
| `empresa.logo_en_oscuro` | no | | `chip` (placa blanca, por defecto) o `blanco` (pinta el logo blanco; solo logos de un color sin fondo). |
| `empresa.logo_en_naranja` | no | | `chip` (por defecto) o `directo`. |
| `angulo` | no | | «A · Equipo propio», etc. (va a fuentes.md). |
| `remitente` | no | | `benjamin` (por defecto) o `nicol`, de remitentes.json. |
| `fecha` | no | 20 | «Noviembre 2026». Por defecto, el mes actual. |
| `fuentes` | sí | | Lista de `{ "dato": "...", "url": "..." }`, con la URL exacta de la página. |
| `por_confirmar` | no | | Lista de textos que quien firma debe revisar antes de enviar. |

## Diapositivas

Cada diapositiva numerada acepta `eyebrow` (40) para cambiar su rótulo chico.

| Campo | Obligatorio | Largo | Notas |
|---|---|---|---|
| `portada.titular` | sí | 95 | |
| `portada.bajada` | sí | 230 | |
| `portada.nota` | no | 60 | Reemplaza «Propuesta para <empresa> · <fecha>» arriba a la derecha de la portada (por ejemplo «Para <empresa> · <fecha>» en un deck sin propuesta). |
| `portada.imagen` | no | | Foto de fondo de la portada. Por defecto, un taller de oficios. `"ninguna"`: fondo oscuro sin foto (mejor para aseo, belleza, eventos u oficios lejos de la reparación). O un archivo de la carpeta, solo si Fixero tiene derechos sobre la foto (nunca una de su sitio). |
| `punto_de_partida.titulo` | sí | 95 | Dos líneas. |
| `punto_de_partida.datos[]` | sí, 3 o 4 | `cifra` 12, `texto` 75 | |
| `punto_de_partida.cita` | no | `texto` 95, `fuente` 60 | Sin cita, la lista va en dos columnas. |
| `punto_de_partida.lista_titulo` | sí | 60 | |
| `punto_de_partida.lista[]` | sí, 3 a 5 (6 sin cita) | `icono`, `texto` 52 con cita / 70 sin cita | Más de 52 con cita hace dos líneas por ítem. |
| `fixero_rubro` | sí | `icono`, `titulo` 24, `texto` 80 | El tercer bloque de «Fixero en una página»: su oficio en Fixero. |
| `fixero_titulo` | no | texto 115 | Reemplaza el título de «Fixero en una página» («La app chilena para…»), por ejemplo para una empresa de otro país. |
| `propuesta.titulo` / `bajada` | sí | 100 / 190 | |
| `propuesta.pilares[]` | sí, 3 | `icono`, `titulo` 34, `texto` 210 | |
| `como_funciona.titulo` | sí | 50 con dos teléfonos, 80 con uno | La columna de texto es angosta con dos teléfonos. |
| `como_funciona.telefonos` | sí | | 1 o 2 de: `tablero`, `tecnico`, `cliente`, `perfil`. |
| `como_funciona.pasos[]` | sí, 3 a 5 | `icono`, `titulo` 42, `texto` 100 (150 con un teléfono) | |
| `beneficios.titulo` | sí | 70 | |
| `beneficios.items[]` | sí, 6 u 8 | `icono`, `titulo` 30, `texto` 115 con 8 / 150 con 6 | |
| `marca` | no | | Diapositiva opcional. `titulo` 80, `telefono` (por defecto `perfil`), `puntos[]` 3 o 4 con `icono`, `titulo` 42, `texto` 160. |
| `antes_despues` | no | | Diapositiva opcional. `titulo` 80, `col_hoy` 28 (por defecto «Coordinación manual»; en el ángulo B usa «Hoy»), `filas[]` 4 a 8 con `tema` 16, `hoy` 52, `con_fixero` 54. |
| `seguridad.titulo` | no | 85 | Por defecto «Quien entra a una casa por Fixero está verificado.». En A y C, mejor «Quien entra a una casa con el nombre <empresa> está verificado.». |
| `seguridad.tarjetas` | no | | 6 claves de: `personas`, `empresa`, `codigo`, `apertura` (solo cerrajería), `sec` (gas y electricidad), `pago`, `garantia`, `fotos`, `reclamos`, `dinero`; o un objeto `{icono, titulo 34, texto 120}`. Por defecto `personas, empresa, codigo, pago, reclamos, garantia`. |
| `alianza` | no | | Diapositiva opcional antes de la reunión, para una alianza más grande que sumarse como empresa (una sociedad, llevar Fixero a otro país). `titulo` 100, `nota` 110 (di que las condiciones se conversan en la reunión), `opciones[]` 3 a 5 de la más chica a la más grande, cada una con `titulo` 34, `texto` 150 y opcionales `etiqueta` 24 y `recomendada: true`. Sin precios, porcentajes ni repartos. |
| `reunion.titulo` | sí | 95 | |
| `reunion.mostraremos[]` | sí, 3 o 4 | `titulo` 40, `texto` 125 | Empieza por «La app en vivo». |
| `reunion.ideas_titulo` | no | 34 | Por defecto «Ideas para conversar». |
| `reunion.ideas[]` | sí, 2 a 4 | `icono`, `titulo` 40, `texto` 85 | Lo no construido va aquí. |
| `cierre.titular` | no | 40 | Por defecto «Agendemos 30 minutos.». |
| `cierre.bajada` | sí | 160 | |

## Teléfonos (`telefonos.<nombre>`)

Solo se arman los que usan `como_funciona.telefonos` o `marca.telefono`. Todos llevan la leyenda «datos de ejemplo». Lo que no cabe dentro de la pantalla lo marca la revisión.

**`tablero`** · el tablero del administrador (ángulos A y C)
- `dias[]`: 1 o 2, cada uno con `dia` (16, «Lunes 2 nov») y `trabajos[]` (1 a 3; 5 en total como máximo).
- Cada trabajo: `titulo` 34, `hora` 16 («09:00 a 10:30»), `quien` 18 (vacío = «Sin asignar»), `comuna` 16, `origen` (`propio` o `fixero`), `estado` (`terminado`, `en_camino`, `trabajando`, `asignado`, `sin_asignar`).
- Un trabajo `fixero` + `sin_asignar` muestra el aviso «1 pedido de Fixero espera a alguien».

**`tecnico`** · el Inicio del técnico de una empresa que asigna (A y C)
- `nombre` 14.
- `hoy[]` 1 o 2 y `manana[]` 0 a 2, cada uno con `titulo` 34, `hora` 16, `direccion` 40, `estado`.

**`cliente`** · lo que ve el cliente con el maestro en camino (sobre todo B)
- `maestro` 18 («Héctor R.»), `oficio` 18, `trabajo` 40 (qué se pidió), `hora` 5 (llegada, por defecto «10:24»).
- `insignia` 34: por defecto «Empresa verificada · <empresa>». En el ángulo B los maestros no son de la marca: usa una insignia real como «Licencia SEC · Clase D» o «Identidad verificada».
- `insignia_icono`: por defecto `buildings`; por ejemplo `lightning`, `identification-card`, `seal-check`.

**`perfil`** · el perfil de la empresa en la app del cliente (A y C)
- Usa `empresa.descripcion`, `empresa.rubro` y las comunas.
- `precios[]` 0 a 3 con `nombre` 34, `detalle` 30 y `precio` 12 (vacío = «Cotizar»).
- `equipo[]` 0 a 2 con `nombre` 18 y `nota` 4 («4,9»).
- Con descripción larga, deja un solo precio o una sola persona del equipo: la revisión avisa si algo queda debajo del botón.

**Deck sin propuesta.** Cuando piden un deck que solo presente a Fixero («que nos conozcan», sin propuesta comercial), omite `punto_de_partida`, `propuesta` y `reunion` (y `marca`, `antes_despues`, `alianza`). Usa `portada.nota` y textos de ejemplo de Fixero, no de la empresa. Quedan la portada, «Fixero en una página», «Cómo funciona», los beneficios, la seguridad y el cierre.
