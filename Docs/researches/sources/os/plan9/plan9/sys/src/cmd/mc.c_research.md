# File Research: sources/os/plan9/plan9/sys/src/cmd/mc.c

Implements `mc`, a columnating command.

Behavior:
- Reads lines from stdin or files into a rune buffer.
- Computes display width of each line using either rune count or actual font metrics.
- Lays words/lines into columns within `linewidth`.
- Option `-` breaks/flushes on colon-newline patterns.
- Numeric `-WIDTH` sets output width.
- `-t` handling is present but initializes `tabflag` to `0`; tabs are enabled automatically only when display/font width is detected.

Key functions:
- `readbuf()` reads runes, expands tabs to spaces, and handles colon-triggered flushes.
- `scanwords()` splits buffered lines into null-terminated words.
- `columnate()` computes column count and emits formatted output.
- `getwidth()` discovers Acme/window font and width to use pixel widths.
- `morechars()` grows the rune buffer.

Dependencies:
- Plan 9 `Bio`, `draw`, font APIs, `/dev/acme`, `/dev/window`, and environment variables `font`/`tabstop`.
