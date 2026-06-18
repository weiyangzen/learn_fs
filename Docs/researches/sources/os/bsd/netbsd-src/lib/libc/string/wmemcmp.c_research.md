# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemcmp.c

Implements `wmemcmp(s1, s2, n)`. It compares `n` wide elements, returning zero for equality or `1`/`-1` based on the first differing `__nbrune_t` values.

It avoids subtracting directly because `wchar_t` may be unsigned.
