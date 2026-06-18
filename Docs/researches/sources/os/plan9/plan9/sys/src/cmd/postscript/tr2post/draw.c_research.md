# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/draw.c

Purpose: Translates troff drawing commands and path grouping commands into PostScript drawing procedure calls.

Key behavior:
- `draw` handles line, circle, ellipse, arc, and spline/wiggly-line commands.
- `drawspline` converts troff spline points to `Ds` prologue procedure calls.
- Updates `hpos`/`vpos` to troff’s expected current point after drawing.
- `beginpath` starts composite paths, emits `gsave`, `newpath`, current move, and sets `/inpath`.
- `drawpath` ends composite paths and either copies raw PostScript or parses friendly path attributes.
- `parsebuf` recognizes stroke/fill variants, gray, color, line width, reverse path, and quoted PostScript passthrough.

Dependencies and integration:
- Depends on drawing procedures from the PostScript prologue, and `pageon`, `endstring`, global position state, and `drawflag`.

Risks and notes:
- `parsebuf` mutates the input buffer and silently ignores unknown tokens.
- Fixed local point arrays limit spline command length.
- Color support assumes a PostScript color dictionary is present.
