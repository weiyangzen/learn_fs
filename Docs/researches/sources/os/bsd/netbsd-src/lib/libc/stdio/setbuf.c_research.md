# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuf.c

Implements `setbuf(FILE *, char *)` as a compatibility wrapper around `setvbuf()`. A non-null buffer requests full buffering with `BUFSIZ`; a null buffer requests unbuffered mode.

The function discards the `setvbuf()` return value because `setbuf()` has a void interface.
