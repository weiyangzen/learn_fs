# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemmove.c

Implements `wmemmove(d, s, n)` by calling `memmove(d, s, n * sizeof(wchar_t))`. It returns the destination as `wchar_t *`.

This provides overlap-safe wide-element movement via the byte `memmove` implementation.
