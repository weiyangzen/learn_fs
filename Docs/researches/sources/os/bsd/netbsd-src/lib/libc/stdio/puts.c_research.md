# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/puts.c

Implements `puts()` by building a two-element write vector for the string and trailing newline, then calling `__sfvwrite(stdout, &uio)` under the stdout lock. A null pointer is treated as the literal string `"(null)"`.

It returns `'\n'` on success or `EOF` on write failure.
