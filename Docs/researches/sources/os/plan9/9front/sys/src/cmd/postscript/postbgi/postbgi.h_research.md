# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.h

`postbgi.h` defines the BGI opcode constants, byte decoding masks, drawing mode constants, line style tables, color component selectors, and small helper structs used by `postbgi.c`.

Key contents:
- BGI opcodes include character modes, graph mode, subroutines, page end, repeat, absolute positioning, vectors, rectangles, points, line plot, character size, line style, arcs, filled shapes, raster rectangle, color, trapezoid, and pattern.
- Byte decoding macros distinguish opcode/data bytes: `CHMASK`, `DMASK`, `MSB`, `SGNB`, `MSBMAG`.
- Vector mode constants identify Manhattan x/y alternation, long vectors, and short vectors.
- `OUTLINE`/`FILL` control closed path handling.
- `STYLES` maps BGI line style IDs to PostScript dash arrays.
- `get_color()` component selectors are `RED`, `GREEN`, and `BLUE`.
- `Disp` stores subroutine displacement deltas.
- `Fontmap` maps user font aliases to PostScript names.
- `MAG(A, B)` builds a sign-magnitude integer magnitude from two BGI data bytes.
- `LINESPACE(A)` derives text line spacing from BGI character grid size.

This header is tightly coupled to `postbgi.c` and has no standalone behavior.
