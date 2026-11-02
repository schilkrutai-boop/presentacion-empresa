# Cómo escribir el deck

El deck tiene un solo objetivo: que la empresa acepte una reunión de 30 minutos para ver Fixero funcionando con su empresa. No es un contrato ni un manual: muestra que los conocemos, qué ganan y por qué vale la pena verlo en vivo.

## La voz de Fixero

- Español de Chile, claro y concreto. Frases cortas. Un dato vale más que un adjetivo.
- Hablamos de la empresa en tercera persona («<Empresa> elige quién va») y nos dirigimos a ellos como «ustedes» en el cierre («Les mostramos…»). Nunca «tú».
- Sin exageraciones ni muletillas de marketing: nada de «revolucionario», «solución integral», «potencia tu negocio», «el Uber de…», «líder», signos de exclamación o emojis.
- Comillas latinas para textos de la app y citas: «Voy en camino», «La empresa asigna los trabajos».
- Montos con punto de miles y sin decimales: $25.000. Horas «09:00 a 10:30». Fechas «lunes 9 nov».
- Títulos con mayúscula solo al inicio y en nombres propios. Terminan en punto cuando son oraciones.
- Los nombres de pantallas y botones, tal como en la app: «Tablero de trabajos», «¿Quién va?», «Nuevo trabajo», «Mi empresa», «Pedir cotización a <empresa>».

## Diapositiva por diapositiva

| # | Diapositiva | Qué tiene que lograr |
|---|---|---|
| 1 | Portada | Un titular que nombre a la empresa y lo que gana, en una línea de valor. Bajada: qué proponemos, en una o dos frases. |
| 2 | Lo que vimos | Que se reconozcan: 3 o 4 datos de ellos con cifra grande, una cita corta de su sitio y la lista de lo que hoy implica cada trabajo. El título dice dónde está la oportunidad. |
| 3 | Fixero en una página | Fija. Solo eliges el tercer bloque (`fixero_rubro`): su oficio en Fixero. |
| 4 | La propuesta | Qué les ofrecemos, en tres pilares según el ángulo. |
| 5 | Cómo funcionaría | El flujo de un trabajo en su empresa, con sus servicios y sus comunas en los teléfonos. |
| 6 | Beneficios | 6 u 8 beneficios concretos para la empresa. Cada uno, una función real (referencias/fixero.md). |
| 7 | Su marca (opcional) | Cómo se ve la empresa dentro de Fixero: insignia, perfil, enlace. |
| 8 | Lo que cambia (opcional) | Hoy versus con Fixero, 5 a 8 filas. Respetuoso con cómo trabajan hoy. |
| 9 | Seguridad y confianza | Fija en sus textos; eliges las 6 tarjetas y el título. |
| 9 bis | Cómo trabajar juntos (opcional, `"alianza"`) | 3 a 5 opciones de alianza (A, B, C…), de la más chica a la más grande, cada una con título y una frase. Sin precios, porcentajes ni repartos: `"nota"` dice que las condiciones se conversan en la reunión. `"recomendada": true` destaca una, y `"etiqueta"` le pone un rótulo corto. |
| 10 | La reunión | Qué les mostraremos en 30 minutos (3 o 4 pasos, empezando por «La app en vivo») y 2 a 4 ideas para conversar (lo no construido va aquí). |
| 11 | Cierre | «Agendemos 30 minutos.», una bajada y el botón para agendar, con el contacto de quien firma. |

## Teléfonos con datos de ejemplo

Los teléfonos llevan la leyenda «datos de ejemplo». Llénalos con lo que haría esa empresa de verdad: sus servicios con sus nombres, sus comunas, horarios realistas, direcciones plausibles de esas comunas. Nombres de técnicos chilenos comunes con inicial del apellido («Rodrigo S.», «Camila P.»). Nunca nombres reales de su equipo, y evita los nombres de pila de quien firma y de los dueños de la empresa. Los días del tablero: el lunes y el martes de la semana siguiente a la fecha del deck.

## Largos

Los largos sugeridos de cada campo están en `campos.md`. `armar.py` avisa cuando un texto los pasa, y `--revisar` marca en rojo lo que de verdad se sale de su espacio, también dentro de los teléfonos. Si algo se sale, acorta el texto: no cambies el diseño.
