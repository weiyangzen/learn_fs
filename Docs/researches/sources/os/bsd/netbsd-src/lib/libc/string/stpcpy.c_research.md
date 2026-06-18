# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stpcpy.c

Implements `stpcpy(to, from)`. It copies the source string including the terminating NUL and returns a pointer to the written NUL at the end of the destination.

It undefines fortified macro replacement when `_FORTIFY_SOURCE` is active so this file can provide the real symbol.
