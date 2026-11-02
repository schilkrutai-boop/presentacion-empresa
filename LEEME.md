# Skill «presentacion-empresa» · Fixero

Le pides a Claude una presentación para una empresa y la arma sola, con el diseño del deck que le hicimos a Scanavini:

1. Investiga en internet qué hace la empresa (servicios, comunas, cómo trabaja hoy) y anota la fuente de cada dato.
2. Busca y elige su logo.
3. Decide qué ofrecerle: entrar con su equipo propio, que los maestros de Fixero instalen lo que vende, o una mezcla.
4. Arma 11 diapositivas: lo que vimos de ellos, qué es Fixero, la propuesta, cómo funcionaría (con sus servicios en las pantallas de la app), beneficios, seguridad, y un cierre para **agendar una reunión de 30 minutos** con quien firma.
5. Revisa que nada se salga de su espacio y entrega un PDF y un HTML.

## Instalar

**En Claude Code** (la app de escritorio, pestaña Code, o la terminal), en un Mac:

```bash
unzip presentacion-empresa.zip -d ~/.claude/skills/
```

Queda en `~/.claude/skills/presentacion-empresa/`. Abre una sesión nueva y ya está.

Necesita Python 3 (viene con el Mac) y Google Chrome instalado: Chrome se usa sin abrir ventanas para sacar el PDF y las capturas de revisión.

**Desde GitHub** (así recibes las actualizaciones). Con acceso al repo privado:

```bash
git clone https://github.com/schilkrutai-boop/presentacion-empresa.git ~/.claude/skills/presentacion-empresa
```

Si ya la habías instalado con el zip, borra antes esa carpeta. Para actualizarla: `git -C ~/.claude/skills/presentacion-empresa pull`.

**En claude.ai:** Configuración → Capacidades → Skills → subir `presentacion-empresa.zip` (con «Ejecución de código» activada). Ahí puede que no logre bajar el logo o sacar el PDF; en ese caso entrega el HTML: se abre en el navegador y se imprime como PDF (márgenes «Ninguno», «Gráficos de fondo» activado).

## Usar

Escríbele a Claude, por ejemplo:

- `/presentacion-empresa Clean & Go`
- «Hazle una presentación a Albin Trotter (albintrotter.com), firma Nicol»
- «Haz las presentaciones de las empresas de Piscinas de empresas-tipo-scanavini.csv»

Por defecto firma Benjamin. Para que firme Nicol, dilo en el pedido («firma Nicol»). El botón del cierre abre WhatsApp hacia quien firma con un mensaje listo para agendar.

Cada empresa queda en `presentaciones/<Empresa>/`:

| Archivo | Qué es |
|---|---|
| `Fixero-<Empresa>.pdf` | Para mandar por correo. |
| `Fixero-<Empresa>.html` | La misma presentación en un solo archivo: flechas para avanzar, F para pantalla completa; en el celular se lee con scroll. |
| `fuentes.md` | De dónde salió cada dato y lo que hay que **confirmar antes de enviar**. |
| `empresa.json` | Los textos. Si quieres cambiar algo, pídeselo a Claude o edítalo y vuelve a armar. |

## Antes de enviar una presentación

- Lee `fuentes.md`, sobre todo «Por confirmar».
- Mira el PDF completo: los datos de la empresa tienen que ser ciertos y el logo tiene que verse bien.
- La presentación no habla de precios ni comisiones: eso se conversa en la reunión.
- Claude nunca envía nada: tú mandas el PDF.

## Cambiar algo de la skill

- Datos de contacto de quien firma, o un enlace para agendar (Calendly, Google Calendar): `remitentes.json`. Si `agenda_url` tiene un enlace, el botón dice «Agendar la reunión» y lleva ahí.
- Lo que se puede decir de Fixero (funciones, lo que no está construido): `referencias/fixero.md`. Mantenlo al día cuando Fixero lance algo.
- Cómo se escribe y qué lleva cada diapositiva: `referencias/escritura.md` y `referencias/angulos.md`.
