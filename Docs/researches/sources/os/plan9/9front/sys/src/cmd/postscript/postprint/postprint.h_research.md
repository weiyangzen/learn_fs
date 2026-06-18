# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.h

Header for `postprint.c`. It defines default page/text settings (`LINESPP=66`, `TABSTOPS=8`, `POINTSIZE=10`), the `Fontmap` mapping type, and `FONTMAP`, which maps troff-like and short names such as `R`, `I`, `B`, `CW`, `courier` to Courier PostScript fonts.

Integration points:
- Included only by `postprint.c`.
- `FONTMAP` must end with `{NULL, NULL}` for `get_font`.

Risks:
- Declares only `char *get_font();`, using old-style prototypes.
- Defaults assume constant-width fonts; proportional fonts are allowed but documented as unreliable for layout.
