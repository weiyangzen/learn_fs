# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_rindex.c

Lint stub for legacy `rindex()`. It returns NULL.

The runtime implementation is supplied through the `strrchr.c` inclusion wrapper.
