# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.c

BGI (Basic Graphical Instructions) to PostScript translator.

Key responsibilities:
- Emits DSC headers, copies the PostScript prologue, handles setup, translates BGI input streams, emits trailer/accounting.
- Parses options for aspect ratio, copies, font, magnification, forms-per-page, page ranges, orientation, line width, offsets, accounting, extra files, encoding, prologue, raw PostScript patches, special requests, debug, and ignore-fatal mode.
- Decodes BGI opcodes for text modes, graph mode, pages, coordinates, points, vectors, rectangles, arcs, filled rectangles/trapezoids, line styles, colors, patterns, character size, subroutines, and calls.
- Manages current BGI position, page counters, subroutine displacement tracking, and output redirection for selected pages.

Important behavior:
- `header()` pre-scans `-L` to choose the prologue before writing DSC/prologue output.
- `formfeed()` closes the current page, skips nulls, chooses stdout or `/dev/null` for the next page, emits setup, and resets size/position.
- Subroutines become PostScript procedures `S<num>` inside `%%BeginGlobal`/`%%EndGlobal`.
- Vectors accumulate relative displacements on the stack, then call prologue procedure `v`.
- Colors convert BGI cyan/yellow/magenta-style bytes into RGB triples.
- Patterns are approximated by averaging four BGI color bytes.
- Repeats and raster rectangles are not implemented.

Dependencies:
- Uses shared PostScript common files and prologues: `comments.h`, `gen.h`, `path.h`, `ext.h`, `request.c`, and `postbgi.h`.

Notable risks:
- Old K&R style with many implicit-int functions.
- Several unimplemented BGI features are fatal.
- `arc(FILL)` ignores fill mode and emits stroked `arcn`.
- Page counting/output routing is subtle because skipped pages write to `/dev/null`.
