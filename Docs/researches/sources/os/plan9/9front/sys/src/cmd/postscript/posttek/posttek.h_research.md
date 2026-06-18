# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.h

Header for `posttek.c`. It defines Tektronix 4014 ASCII/control constants, display state constants, pen states, screen coordinate maxima, special point intensity table, character size tables, line-style arrays, a `Point` struct, and the same Courier-centric `Fontmap` mapping style used by other translators.

Integration points:
- `CHARHEIGHT`, `CHARWIDTH`, `TEKFONT`, `INTENSITY`, and `STYLES` initialize global arrays in `posttek.c`.
- `OUTMODED` is a sentinel returned by parser/control helpers.

Risks:
- Style arrays are string PostScript snippets embedded in C; comments note they belong in the prologue.
- Fixed coordinate assumptions approximate but do not exactly model the real terminal dimensions.
