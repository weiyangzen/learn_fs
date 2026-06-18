# File Research: sources/os/bsd/netbsd-src/lib/libc/string/memccpy.c

Implements `memccpy(dst, src, c, n)` with a straightforward byte copy loop. It copies until either `n` bytes are exhausted or the copied byte equals `c`; on match it returns the destination pointer just past that byte.

If no byte matches, it returns NULL.
