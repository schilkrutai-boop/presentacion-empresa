# presentacion-empresa · Skill de Claude para Fixero

Arma la presentación de Fixero para una empresa, o una por empresa para una lista, con el diseño del deck Fixero × Scanavini. Investiga qué hace la empresa, busca su logo, elige qué ofrecerle y entrega un PDF y un HTML cuyo objetivo es conseguir una reunión.

## Instalar en Claude Code (Mac)

```bash
git clone https://github.com/schilkrutai-boop/presentacion-empresa.git ~/.claude/skills/presentacion-empresa
```

Abre una sesión nueva de Claude Code y escribe `/presentacion-empresa <empresa>`. Si ya la habías instalado con el zip, borra antes esa carpeta.

Para recibir los cambios:

```bash
git -C ~/.claude/skills/presentacion-empresa pull
```

Necesita Python 3 y Google Chrome. Cómo usarla, qué revisar antes de enviar una presentación y cómo cambiar la skill está en [LEEME.md](LEEME.md).

El repo es privado porque `remitentes.json` tiene los datos de contacto de quien firma.
