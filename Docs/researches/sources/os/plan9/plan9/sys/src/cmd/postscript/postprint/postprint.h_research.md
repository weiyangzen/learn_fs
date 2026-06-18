# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.h

Local defaults and font aliases for `postprint`.

Contents:
- Defines default `LINESPP=66`, `TABSTOPS=8`, and `POINTSIZE=10`.
- Defines `Fontmap` structure for user font aliases.
- Defines `FONTMAP` aliases for Courier, Courier-Oblique, and Courier-Bold.
- Declares `char *get_font()`.

Role:
- Supplies default text layout settings and fixed-width PostScript font aliasing used by `postprint.c`.

Risks and quirks:
- Comments state only constant-width fonts are guaranteed to work well, but the translator allows arbitrary font names when lookup fails.
