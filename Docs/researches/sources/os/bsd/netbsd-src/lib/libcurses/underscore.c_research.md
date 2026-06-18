# File Research: sources/os/bsd/netbsd-src/lib/libcurses/underscore.c

This file implements old curses underscore/underline mode helpers.

Key entry points:
- `underscore()` and `underend()` operate on `stdscr` when `_CURSES_USE_MACROS` is not set.
- `wunderscore(WINDOW *)` enables `__UNDERSCORE` in `win->wattr` when the terminal can enter/exit underline mode or has an underline character capability.
- `wunderend(WINDOW *)` clears `__UNDERSCORE` when `exit_underline_mode` is available.

Integration:
- Uses termcap/terminfo globals such as `enter_underline_mode`, `exit_underline_mode`, and `underline_char`.
- Modifies window attribute state; later rendering code emits terminal capabilities.

Risks and notes:
- Returns `1` on success-like paths rather than the usual curses `OK` constant, matching legacy behavior in this file.
- `wunderend()` only clears when `exit_underline_mode` exists, so underline state may remain if only underline-character fallback is available.
