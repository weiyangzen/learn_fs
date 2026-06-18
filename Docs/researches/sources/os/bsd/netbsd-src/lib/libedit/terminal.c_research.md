# File Research: sources/os/bsd/netbsd-src/lib/libedit/terminal.c

## Purpose
Implements libedit's terminal capability and display-output layer. It loads termcap/curses capabilities, tracks screen geometry, manages display buffers, emits cursor/control sequences, and binds terminal arrow keys into libedit key macros.

## Main Components
- Termcap capability tables `tstr[]` and `tval[]` enumerate string and boolean/numeric capabilities such as cursor movement, insert/delete, clear-to-EOL, auto margins, tabs, meta key, rows, and columns.
- `terminal_init()` allocates terminal buffers, capability arrays, and function-key metadata, then calls `terminal_set()` and initializes arrow defaults.
- `terminal_set()` reads `$TERM`, falls back to `dumb`, calls `tgetent/tgetstr/tgetflag/tgetnum`, blocks `SIGWINCH` while changing terminal state, updates flags, window size, and key bindings.
- `terminal_change_size()`, `terminal_get_size()`, and display buffer helpers allocate and reallocate `el_display` and `el_vdisplay` after size changes.
- Cursor/output operations include `terminal_move_to_line()`, `terminal_move_to_char()`, `terminal_overwrite()`, `terminal_insertwrite()`, `terminal_deletechars()`, `terminal_clear_EOL()`, `terminal_clear_screen()`, `terminal_beep()`, `terminal_writec()`, `terminal__putc()`, and `terminal__flush()`.
- Arrow-key handling includes default arrow bindings, VT escape fallback sequences, termcap-derived escape sequences, and user-visible print/set/clear operations.
- User commands `terminal_telltc()`, `terminal_settc()`, `terminal_gettc()`, and `terminal_echotc()` expose terminal capabilities to libedit command processing.

## Integration
This file is called by refresh/rendering code, tty setup, keymacro handling, and command parsing. It depends on `el.h`, `fcns.h`, termcap/curses APIs, multibyte conversion helpers, and internal edit state.

## Risks / Notes
- The termcap string pool is fixed at `TC_BUFSIZE` and compacts manually.
- Output via `tputs()` uses a static `terminal_outfile`; `_REENTRANT` builds guard it with a mutex.
- Several operations trust `el->el_display` and cursor state to be accurate; comments explicitly warn updates will be wrong if the screen model is stale.
- Terminal size assignment has unusual `t_size.v = Val(T_co)` / `t_size.h = Val(T_li)` before `terminal_change_size()` corrects geometry through line/column parameters.
