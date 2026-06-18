# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarray.c

Implements OpenBSD-style `reallocarray(optr, nmemb, size)` on top of `reallocarr()`. It handles zero dimensions with `realloc(optr, 0)`, returns the new pointer on success, maps overflow to `errno = ENOMEM`, and otherwise forwards the allocation error.

The original pointer remains unchanged on failed nonzero resize.
