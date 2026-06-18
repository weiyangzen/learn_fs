# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strndup.c

Implements `strndup(str, n)` when unavailable from the host. It measures at most `n` bytes, allocates `len + 1`, copies that many bytes, and appends a NUL.

It never reads beyond the first NUL or the `n` limit.
