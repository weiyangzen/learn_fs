# File Research: sources/os/bsd/netbsd-src/lib/libcurses/refresh.c

Implements the core curses refresh engine: `refresh`, `wnoutrefresh`, `pnoutrefresh`, `wrefresh`, `prefresh`, `doupdate`, and terminal diff helpers.

`_wnoutrefresh` copies dirty regions from windows or pads into `__virtscr`, handles subwindow and derived-window propagation, copies wide-cell continuation metadata, updates virtual cursor/flags, and clears source dirty ranges. `doupdate` compares `__virtscr` with `curscr`, optionally clears the screen, hashes dirty lines, applies scroll optimization through `quickch`, updates changed lines with `makech`, respects typeahead polling, handles `__LEAVEOK`, and flushes output.

The low-level path manages attributes/colors (`putattr`, `putattr_out`, `__unsetattr`), emits characters and non-spacing chains (`putch`, `__cursesi_putnsp`), handles bottom-right/autowrap hazards (`putchbr`), optimizes clear-to-EOL, and uses terminal insert/delete/scroll capabilities in `scrolln`. It is the central consumer of dirty flags, hashes, line contents, terminal capabilities, color state, wide cell widths, and cursor state.
