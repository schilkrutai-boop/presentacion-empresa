# Ángulos: qué le ofrecemos a cada tipo de empresa

Elige un ángulo por empresa según lo que encontraste en la investigación. El ángulo decide la propuesta, los teléfonos de las diapositivas y las ideas para conversar. Anótalo en `"angulo"` del JSON (por ejemplo, `"A · Equipo propio"`).

| Ángulo | Cómo reconocerla | Lo que le ofrecemos |
|---|---|---|
| **A · Equipo propio** | Presta el servicio con su gente: aseo, control de plagas, piscinas, jardines, climatización, mantenciones, mudanzas, servicio técnico propio. | Entrar como empresa verificada con todo su equipo: ordenar sus trabajos en el tablero y recibir clientes nuevos de Fixero. |
| **B · Vende, Fixero instala** | Vende productos que alguien tiene que instalar, reparar o mantener, y no tiene equipo propio o deriva a técnicos independientes (marcas, importadores, tiendas especialistas, retail). | La red de maestros verificados de Fixero atiende a sus clientes, con pago protegido y garantía. |
| **C · Mixto** | Vende e instala, pero con un equipo chico para su demanda (como Scanavini: 3 instaladores para 32 comunas). | A + B: su equipo entra como empresa verificada y los maestros de Fixero suman capacidad. |
| **D · Plataforma** | Es un marketplace o app de servicios: un posible competidor. | **No armes el deck.** Avisa a quien lo pidió y pregunta si igual quiere hacerlo. |

Ante la duda entre A y C, pregúntate si su equipo alcanza para lo que venden. Ante la duda entre B y C, mira si tienen técnicos en planilla (empleos publicados, «nuestros técnicos», fotos del equipo con uniforme).

## A · Equipo propio

- **Portada:** su servicio, ordenado y con clientes nuevos. Ej.: «Cada <servicio> de <Empresa>, asignado, seguido y cobrado desde una app.»
- **Propuesta, tres pilares:** «Ordena sus trabajos» (tablero, quién va, avisos), «Recibe clientes nuevos» (los pedidos de Fixero de su oficio y comunas), «Su marca en cada casa» (insignia, perfil con trabajos, precios y reseñas).
- **Cómo funcionaría:** `"telefonos": ["tablero", "tecnico"]`. Pasos: entra el trabajo (cliente propio o de Fixero) → aparece en el tablero → la empresa elige quién va → el técnico lo recibe en su celular → «Voy en camino · Llegué · Terminé».
- **Beneficios (8):** tablero, dos formas de trabajar, avisos de llegada y término, cambiar quién va, cobro asegurado, todo a la cuenta de la empresa, cotizan a su nombre, el equipo en minutos (o boletas en orden, calidad medible con reseñas).
- **Marca:** `"telefono": "perfil"`; puntos: insignia en cada técnico, perfil de empresa, enlace de su perfil para su web e Instagram, búsqueda de su oficio.
- **Antes y después:** agendar, asignar, seguimiento, llegada, extras, cobro, respaldo, clientes nuevos.
- **Seguridad:** `["personas", "empresa", "codigo", "pago", "reclamos", "fotos"]`, con el título «Quien entra a una casa con el nombre <Empresa> está verificado.».
- **La garantía:** la de 30 días de Fixero compromete a su equipo en los pedidos de Fixero. Si ellos dan otra (24 horas, 3 meses), no pongas la tarjeta `garantia`: anótalo en `por_confirmar` para conversarlo.
- **Cuadrillas:** en Fixero cada trabajo tiene una persona a cargo. Si trabajan en cuadrillas (aseo, mudanzas), muestra el trabajo asignado a quien la lidera y anótalo en `por_confirmar`. Todos los que entran a la casa de un cliente de Fixero se verifican.
- **Planes de mantención:** el Plan mensual de Fixero existe solo para piscinas y jardines. Si su negocio son planes de otra cosa (aseo, plagas), va como idea, no como función.
- **`empresa.trabajador`:** cómo llaman a su gente («operaria», «instalador», «supervisora»); sale en la leyenda del teléfono.
- **Ideas para conversar:** Plan mensual con su equipo (solo piscinas y jardines), socio fundador de su categoría en el lanzamiento, sus servicios con precio cerrado en Precio fijo, un piloto en sus comunas.

## B · Vende, Fixero instala

- **Portada:** lo que venden, bien instalado. Ej.: «Cada <producto> de <Marca>, instalado por un maestro verificado y con pago protegido.» Escribe el producto como lo escribe la marca (calefón o calefont).
- **Propuesta, tres pilares:** «Una red de maestros verificados» (identidad, antecedentes, licencia SEC si aplica), «Sus clientes, bien atendidos» (Cotiza, Reserva o Precio fijo, seguimiento, garantía de 30 días, reclamos con mediación), «Su producto en cada orden» (el maestro lo agrega como línea de la cotización u orden de trabajo, el cliente lo aprueba y lo paga con su tarjeta, y queda en el comprobante PDF).
- **Cómo funcionaría:** `"telefonos": ["cliente"]`, con la insignia que corresponda al maestro: «Licencia SEC» con su clase (electricidad: Clase A a D; gas: clase 1 a 3), por ejemplo `"insignia": "Licencia SEC · Clase D"` con `"insignia_icono": "lightning"`; o `"Identidad verificada"` con `"identification-card"`. Nunca «Empresa verificada · <marca>»: los maestros no son de la marca. Pasos: el cliente compra → pide la instalación en Fixero → un maestro verificado la toma → la hace con fotos y orden aprobada → el cliente confirma y califica.
- **Beneficios (6 u 8):** maestros verificados, pago protegido, garantía de 30 días, reclamos con mediación, fotos y comprobante, seguimiento en el mapa, extras aprobados antes, cobertura de Santiago.
- **Marca:** sáltala (sin `"marca"`) salvo que tengan técnicos propios.
- **Antes y después:** compara lo que hacen hoy (una lista de técnicos que no garantizan, «el cliente busca por su cuenta») con Fixero, con `"col_hoy": "Hoy"`. Sé respetuoso: describe, no critiques.
- **Seguridad:** `["personas", "sec", "codigo", "pago", "garantia", "reclamos"]` (cambia `sec` por `fotos` si no es gas ni electricidad), con un título que no diga que los maestros son de la marca: «Quien instala un <producto> por Fixero está verificado.».
- **Cobertura:** si venden en todo Chile, aclara en `por_confirmar` que Fixero atiende Santiago.
- **Ideas para conversar:** «Instalación por Fixero» en su web o un QR en su tienda, sello «Instalador certificado <marca>» para maestros que ellos capaciten, sus instalaciones con precio cerrado, un piloto con sus clientes de Santiago.

## C · Mixto

- Toma A como base (tablero, técnico, perfil) y suma B: en la propuesta, un pilar dice que los maestros de Fixero cubren lo que su equipo no alcanza.
- **Ideas para conversar:** que certifiquen a maestros de Fixero, sus instalaciones en Precio fijo, agendar desde su tienda, socio fundador de la categoría.
- El ejemplo completo es `empresa.ejemplo.json` (Scanavini).

## Íconos por oficio

Todos los íconos son Phosphor (assets/iconos, más de 1.500). Algunos útiles:

| Oficio | Íconos |
|---|---|
| Gasfíter | `drop`, `wrench`, `fire` (calefont) |
| Electricista | `lightning`, `plug`, `lightbulb` |
| Cerrajero | `lock-key`, `key`, `door-open` |
| Carpintero, mueblista | `hammer`, `armchair`, `couch` |
| Pintor | `paint-roller`, `paint-brush` |
| Jardinero | `plant`, `tree`, `leaf` |
| Piscinas | `swimming-pool`, `drop` |
| Aseo | `broom`, `sparkle`, `spray-bottle` |
| Control de plagas | `bug`, `bug-beetle` |
| Climatización | `thermometer`, `snowflake`, `fan`, `wind` |
| Electrodomésticos | `washing-machine`, `oven`, `television` |
| Seguridad | `security-camera`, `shield`, `siren` |
| Construcción | `hard-hat`, `wall`, `ruler` |
| Mecánico, aseo de vehículos | `car`, `wrench`, `engine` |
| Fletes | `truck`, `package` |
| Eventos | `confetti`, `champagne` |
| Belleza | `scissors`, `hand` |
| Cortinas y toldos | `frame-corners`, `sun` |

Para ver si existe uno: `ls <skill>/assets/iconos | grep <palabra>`. Si el nombre no existe, `armar.py` sugiere parecidos.
