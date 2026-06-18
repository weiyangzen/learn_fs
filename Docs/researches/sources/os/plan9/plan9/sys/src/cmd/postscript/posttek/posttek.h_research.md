# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.h

Purpose: Defines Tektronix 4014 constants and data structures used by `posttek.c`.

Key contents:
- ASCII control-code macros from `NUL` through `DEL`.
- Display modes: `OUTMODED`, `ALPHA`, `GIN`, `GRAPH`, `POINT`, `SPECIALPOINT`, `INCREMENTAL`, `RESET`, `EXIT`.
- Pen state constants `UP` and `DOWN`.
- Tektronix coordinate limits `TEKXMAX` and `TEKYMAX`.
- `INTENSITY` table for special point plotting.
- Character size tables `CHARHEIGHT`, `CHARWIDTH`, default `TEKFONT`.
- PostScript line-style dash arrays in `STYLES`.
- `Point` and `Fontmap` structs.
- `FONTMAP` maps shorthand/user font names to PostScript Courier variants.
- Declares `get_font`.

Dependencies and integration:
- Included by `posttek.c`; values directly drive state-machine geometry, text motion, and PostScript line styles.

Risks and notes:
- `STYLES` comment says the values belong in the prologue, but they are embedded in C.
- Font mapping is intentionally small and Courier-oriented.
