# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/plot.c

Interactive/file-driven plot command interpreter.

Key responsibilities:
- Initializes libplot and dispatches abbreviated plot commands to libplot functions.
- Parses numeric arguments, string arguments, polygon point lists, macro definitions, macro calls, and include files.
- Maintains a nested input stack for files and in-memory macro bodies.
- Supports command-line drawing options such as erase, color, fill color, grade, double buffering, and server mode.
- Keeps the window open after drawing, with a mouse menu item to exit.

Important behavior:
- Command names are matched by prefix length from the `plots[]` table.
- Numeric arguments are scaled by the current macro call scale.
- `define` stores macro bodies between braces; `call` pushes the stored string onto the input stack.
- `include` pushes a new `Biobuf` onto the same input stack.
- Lines beginning with `:` are comments.
- `server()` publishes a pipe in `/srv/plot`, but the source comment says it does not work.

Dependencies:
- Uses Plan 9 `bio`, `draw`, `event`, and libplot functions from `plot.h`.

Notable risks:
- Many functions use old implicit-int style.
- Fixed buffers and arrays (`argstr`, `x`, `cnt`, `pts`, macro library) impose hard limits.
- `define()` grows `bstash` with `realloc()` after freeing it first, which is a bug: freeing before `realloc` loses existing contents and can corrupt stored macro bodies.
- Macro name storage has a fixed 512-byte allocation and no growth after first allocation.
