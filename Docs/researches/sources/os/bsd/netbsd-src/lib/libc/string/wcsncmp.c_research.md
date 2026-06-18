# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncmp.c

Implements `wcsncmp()`. It compares up to `n` wide characters, returns zero for `n == 0` or equal prefixes, and returns an ordering based on the first differing `__nbrune_t` values.

It stops early on a matching terminating NUL.
