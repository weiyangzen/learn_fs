# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/ex1.c

Read completely: 342 lines.

Interactive wide-curses exercise program. It initializes locale and curses, replaces `stdscr` with a small custom window, enables cbreak/noecho/scrolling, and then reads raw input commands to exercise many narrow and wide-character APIs.

It tests `add_wch`, `add_wchstr`, `addwstr`, `get_wch`, `get_wstr`, `in_wch`, `in_wchstr`, `inwstr`, `hline_set`, `vline_set`, `border_set`, `box_set`, `bkgrnd`, insertion functions, keypad mode, timeout modes, and basic erase/clear/refresh operations. It constructs `cchar_t` values with multiple elements and attributes to stress combining/nonspacing handling.

This is not polished application code: it uses old-style `main()`, hardcoded multibyte sample strings, fixed buffers, direct `getchar()` in some paths, and manual `delwin()` cleanup. Its role is regression/manual testing for wide curses behavior.
