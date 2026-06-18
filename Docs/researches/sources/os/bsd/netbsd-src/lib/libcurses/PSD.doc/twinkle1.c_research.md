# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle1.c

Read completely: 161 lines.

Curses animation demo that randomly chooses one of four screen patterns and “twinkles” it by drawing all stars in randomized order, then erasing them in another randomized order. Patterns include alternating lines, a border box, checkerboard-like parity, and a center bar.

It initializes curses, ignores cursor placement with `leaveok()`, disables echo/newline translation, and loops forever through `makeboard()`, `puton('*')`, and `puton(' ')`. `puton()` shuffles the `Layout` array and calls `mvaddch()` plus `refresh()` for each position, intentionally exercising many small updates.

Exit is via SIGINT handler `die()`, which moves to the lower-left corner using `mvcur()`, calls `endwin()`, and exits. It is documentation/demo code with fixed 80x24 layout assumptions and random animation behavior.
