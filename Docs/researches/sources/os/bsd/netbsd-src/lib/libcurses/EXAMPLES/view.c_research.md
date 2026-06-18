# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/view.c

Read completely: 527 lines.

Small interactive file viewer adapted from ncurses examples. It reads a file into memory, expands tabs, optionally escapes nonprintable bytes in narrow mode, and stores each line as either `chtype` strings or `cchar_t` strings when `HAVE_WCHAR` is enabled.

The UI initializes curses, optional color, keypad input, nonblocking input, and insert/delete-line optimization. Commands scroll up/down, jump home/end, shift horizontally, set delay modes, and quit. Numeric prefixes repeat motion commands. `show_all()` redraws a status/header line with filename, terminal size, shift, current time, and visible file lines.

Wide-character mode converts multibyte input with `mbrtowc()`, builds complex characters with `setcchar()`, and uses `get_wch()`/`add_wchstr()`. Risks are example-level: fixed maximum lines, minimal allocation failure handling, direct file slurping, and old portability branches for ncurses/NetBSD curses.
