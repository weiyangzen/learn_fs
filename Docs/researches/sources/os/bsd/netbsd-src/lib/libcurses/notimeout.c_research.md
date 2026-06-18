# File Research: sources/os/bsd/netbsd-src/lib/libcurses/notimeout.c

Implements `notimeout(WINDOW *win, bool bf)`.

It toggles the `__NOTIMEOUT` flag, which affects whether input parsing waits indefinitely while assembling function-key escape sequences.
