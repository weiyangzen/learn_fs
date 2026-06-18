# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/devcntl.c

Device-control command handler for `tr2post`, especially `x` and `x X` commands. It mounts fonts, initializes device resolution/name, applies character height/slant, and routes troff `\X` extensions for pictures, paths, raw PostScript, and unimplemented features.

Integration points:
- Invoked from `conv.c` on `x`.
- Calls `initialize`, `mountfont`, `t_charht`, `t_slant`, `picture`, `beginpath`, `drawpath`.
- Uses globals `devname`, `resolution`, `minx`, `miny`.

Risks:
- Several `x X` commands are fatal “not implemented yet” paths.
- Uses fixed-size buffers for command fragments.
- `Bungetc(inp)` after reading a line is subtle; it only pushes back one byte after copying the line buffer.
