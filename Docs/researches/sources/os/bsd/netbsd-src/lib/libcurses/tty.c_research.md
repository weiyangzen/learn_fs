# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tty.c

This file implements libcurses terminal mode management: raw/cbreak/cooked modes, input timing behavior, echo/newline settings, typeahead, save/restore tty state, screen start/end sequences, and erase/kill character queries.

Key entry points:
- `baudrate()`, `gettmode()`, and `_cursesi_gettmode()` initialize and query terminal mode state.
- `raw()`, `noraw()`, `cbreak()`, `nocbreak()`, and `halfdelay()` switch input modes.
- `__delay()`, `__nodelay()`, `__timeout()`, and `__notimeout()` manipulate `VMIN`/`VTIME`.
- `__save_termios()` and `__restore_termios()` preserve timeout settings.
- `echo()`, `noecho()`, `nl()`, `nonl()`, `intrflush()`, `qiflush()`, and `noqiflush()` control curses terminal behavior flags.
- `__startwin()`, `endwin()`, `isendwin()`, and `flushinp()` manage active curses screen mode.
- `savetty()`, `resetty()`, `erasechar()`, `killchar()`, `erasewchar()`, `killwchar()`, and `typeahead()` provide compatibility APIs.

Important state and control flow:
- `_cursesi_gettmode()` reads terminal attributes from input first, then output, and marks `screen->notty` if neither is a tty.
- It builds three termios templates: `baset`, `cbreakt`, and `rawt`; `rawt` disables signal/extension processing and output post-processing, with hardware/parity handling dependent on `TCSASOFT`.
- Mode setters update global compatibility flags like `__rawmode`, `__pfast`, `__echoit`, and screen-local fields like `useraw`, `curt`, `nl`, and `pfast`.
- `__startwin()` emits alternate-screen/cursor/keypad sequences through terminfo wrappers and optionally installs a larger BSD stdio buffer.
- `endwin()` delegates to `__stopwin()` from `tstp.c`.

Risks and notes:
- Many routines assume `_cursesi_screen` and `stdscr` are valid.
- Timeout helpers change all three termios templates, so callers relying on original `VMIN`/`VTIME` must use the save/restore helpers correctly.
- Non-tty operation returns OK for many mode operations while disabling actual termios changes.
