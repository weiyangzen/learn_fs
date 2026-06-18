# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/devcntl.c

Purpose: Interprets troff `x` device-control commands for `tr2post`.

Key behavior:
- Maintains `devname`, `resolution`, `minx`, and `miny`.
- Handles font mounting, initialization, resolution, device name, character height, slant, and input encoding stubs.
- For `x X ...` extension commands, dispatches picture inclusion, path begin/end, object begin/end, and PostScript passthrough.
- Explicitly fatal-errors on unimplemented extensions: inline pictures, new baseline, draw text, set text, set color, INFO, ExportPS.

Dependencies and integration:
- Calls `mountfont`, `initialize`, `t_charht`, `t_slant`, `picture`, `beginpath`, `drawpath`, and string flushing helpers.
- Consumes full device-control lines and increments `inputlineno`.

Risks and notes:
- Reads extension payload into fixed buffers.
- Several extensions are recognized but deliberately not implemented.
- `Bungetc(inp)` after reading the line is subtle and preserves newline handling for downstream line consumption.
