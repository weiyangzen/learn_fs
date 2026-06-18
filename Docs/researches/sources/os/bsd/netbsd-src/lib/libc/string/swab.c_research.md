# File Research: sources/os/bsd/netbsd-src/lib/libc/string/swab.c

Implements `swab(src, dst, nbytes)`, copying bytes in swapped pairs. It ignores a final odd byte and returns immediately for lengths <= 1.

Although POSIX leaves overlapping behavior undefined, the implementation explicitly preserves `swab(ptr, ptr, n)` by loading both source bytes before writing the swapped pair.
