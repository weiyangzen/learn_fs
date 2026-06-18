# File Research: sources/os/bsd/netbsd-src/lib/libc/string/memrchr.c

Implements `memrchr(s, c, n)`. It starts from `s + n` and scans backward byte-by-byte until it finds `c` or exhausts the buffer.

Returns a non-const pointer to the matching byte or NULL.
