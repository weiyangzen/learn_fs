# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/curterm.c

Manages the process-global current terminal state for terminfo/termcap compatibility.

Key responsibilities:
- Defines global `TERMINAL *cur_term`.
- Defines `ttytype[256]`, filled with terminal name, aliases, and description for compatibility with applications that inspect ncurses-style `ttytype`.
- Computes output baud index from `termios` via `_ti_setospeed`.
- Implements current-terminal lifecycle:
  - `set_curterm`
  - `del_curterm`
  - `termname`
  - `longname`

Important behavior:
- `set_curterm` updates global `PC` and `ospeed` for termcap-compatible output routines.
- `del_curterm` frees all heap-backed storage owned by a `TERMINAL`, including compiled capability arrays, user definitions, buffers, and backing area.
- `termname` and `longname` assume `cur_term` is set.

Role in subsystem:
- Bridges the thread-aware `TERMINAL *` API and older global-state terminfo/termcap APIs.
