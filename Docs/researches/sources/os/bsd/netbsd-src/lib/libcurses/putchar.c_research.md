# File Research: sources/os/bsd/netbsd-src/lib/libcurses/putchar.c

Implements low-level terminal output callbacks.

`__cputchar` and `__cputchar_args` write bytes to the current or supplied output `FILE`, flushing after each character for terminal control sequencing. Under `HAVE_WCHAR`, `__cputwchar` and `__cputwchar_args` provide the same behavior for wide characters using `putwc`.
