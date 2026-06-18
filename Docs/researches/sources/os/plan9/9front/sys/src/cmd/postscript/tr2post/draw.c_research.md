# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/draw.c

Drawing support for `tr2post`. It translates troff drawing functions into PostScript procedures for lines, circles, ellipses, arcs, and splines, and supports grouped path construction via `BeginPath`/`DrawPath`.

Key behavior:
- `draw` handles `D l`, `D c`, `D e`, `D a`, `D q`, and `D ~`.
- `drawspline` converts troff spline points into PostScript-friendly control data emitted as `Ds`.
- `beginpath` emits `gsave`, `newpath`, current move, and `/inpath true`.
- `drawpath` finalizes a path and either copies raw PostScript or parses simplified tokens.
- `parsebuf` recognizes stroke/fill variants, gray/color/line settings, reversepath, and quoted raw PostScript.

Integration points:
- Sets `drawflag`, which causes `tr2post.c` to include the draw prologue.
- Called from `conv.c` and `devcntl.c`.

Risks:
- `parsebuf` declares `char *p` but enters `for(; p != nil; p = q)` without initializing `p = buf`; this appears to be a real latent bug.
- Fixed arrays in spline parsing cap point count at 100 without explicit overflow reporting.
- Path parser mutates the input buffer and silently ignores unknown tokens.
