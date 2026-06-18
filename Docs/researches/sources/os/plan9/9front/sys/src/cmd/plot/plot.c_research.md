# File Research: sources/os/plan9/9front/sys/src/cmd/plot/plot.c

`plot.c` is the interactive/windowed plot command interpreter. It defines command abbreviations, parses input from files, stdin, definitions, includes, or a `/srv/plot` pipe, and dispatches commands to libplot functions.

The interpreter supports numbers, strings, polygon/control-point lists, comments, dot-prefixed numeric handling, command abbreviation matching, macro-like `define`/`call`, scaling call arguments, and nested includes. It initializes Plan 9 draw output, creates a mouse/keyboard process, handles resize redraws, and exits on menu or keyboard commands.

Global static buffers bound argument and point storage (`NARGSTR`, `NX`, `NPTS`), so malformed or very large inputs can hit explicit fatal limits. The `server()` helper is marked as not working in a comment.
