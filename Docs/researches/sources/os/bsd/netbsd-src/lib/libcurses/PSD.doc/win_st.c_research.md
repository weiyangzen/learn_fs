# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/win_st.c

Read completely: 56 lines.

Documentation excerpt defining the historical internal `WINDOW` structure as `struct _win_st`. Fields include cursor position, max/begin coordinates, flags, character offset, clear/leave/scroll booleans, line storage, first/last changed-column arrays, and linked/original window pointers.

It also defines old internal flag constants such as `_ENDLINE`, `_FULLWIN`, `_SCROLLWIN`, `_FLUSH`, `_FULLLINE`, `_IDLINE`, `_STANDOUT`, and `_NOCHANGE`.

This is explanatory documentation for historical curses internals, not the active NetBSD `WINDOW` definition used by current `libcurses`.
