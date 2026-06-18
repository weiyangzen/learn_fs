# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.c

`postbgi.c` is a BGI (Basic Graphical Instructions) to PostScript translator. It reads a byte-oriented BGI command stream from stdin or named files and emits DSC-structured PostScript built around the `postbgi.ps` prologue.

Main flow:
- `main()` initializes signal handling, writes DSC header/prologue, parses options, runs setup, converts each input, emits trailer/accounting.
- `header()` scans `-L` early to choose the prologue, emits conforming comments, copies the prologue, and opens setup.
- `options()` handles layout, page list, font, copy count, offsets, line width, encoding, raw PostScript pass-through, request injection, debug, and ignore-fatal modes.
- `conv()` is the BGI interpreter loop. It switches on opcodes such as character modes, graph mode, subroutine definition/call, page end, position changes, vectors, rectangles, points, lines, arcs, colors, trapezoids, patterns, and character size.

Important state:
- `hpos`/`vpos` track current BGI coordinates.
- `bgisize` and `linespace` drive text sizing.
- `fp_out` is redirected to stdout or `/dev/null` via page selection.
- `displacement[64]` records subroutine relative movement so calls update the current coordinate.
- `fontmap[]` maps short printer font names to PostScript font names.

Implemented drawing:
- Text modes emit escaped PostScript strings through `t`.
- Vectors emit relative displacement stacks for PostScript procedure `v`.
- Rectangles, trapezoids, points, lines, arcs, colors, and averaged pattern colors are translated into prologue calls/operators.
- Subroutines are emitted as PostScript procedures named `S<id>` inside DSC global sections.

Limitations and risks:
- `BREP` repeat and `BRASRECT` raster rectangle are explicitly fatal/unimplemented.
- Filled arcs/slices are not truly filled; `arc()` always emits `arcn stroke`, ignoring `mode`.
- Color mixing cannot match BGI semantics because PostScript overprints fills.
- Parsing assumes valid 7-bit BGI command/data bytes and uses old K&R C style.
- `repeat()` calls `get_int()` with no argument in old K&R style despite the function taking `highbyte`; this is legacy C behavior and fragile under modern prototypes.

Filesystem relevance: none direct; it is a userland graphics conversion utility in the 9front source tree.
