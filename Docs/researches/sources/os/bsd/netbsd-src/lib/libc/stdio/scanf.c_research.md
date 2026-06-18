# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/scanf.c

Implements `scanf()` and `scanf_l()` as variadic wrappers over `__svfscanf(stdin, ...)` and `__svfscanf_l(stdin, loc, ...)`. Parsing is delegated to `vfscanf.c`.

It provides `scanf_l -> _scanf_l` as a weak alias.
