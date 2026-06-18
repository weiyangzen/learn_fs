# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex2.c

Read completely: 208 lines.

Historical curses screen-manipulation example for the documentation. It fills the screen with numbered rows and repeated digits, then lets the user manipulate the display using simple commands.

Commands include clearing to end of line/bottom/screen, standout on/off, deleting or inserting a one-digit count of lines, cursor movement, home, full refresh, simulated carriage return with insert line and clear-to-EOL, and quit. When movement goes above or below the screen, it inserts/deletes lines and adjusts a logical base row number to simulate scrolling.

The program demonstrates line insertion/deletion, cursor state, scrolling behavior, and refresh calls. It uses old curses interfaces (`crmode()`), K&R-style `main()`, `getchar()`, fixed command parsing, and minimal bounds validation.
