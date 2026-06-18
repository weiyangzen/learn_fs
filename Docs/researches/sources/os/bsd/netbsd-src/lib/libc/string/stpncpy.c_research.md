# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stpncpy.c

Implements `stpncpy(dst, src, n)`. It copies up to `n` characters, zero-fills the remainder if `src` ends early, and returns the position of the terminating NUL when one was copied or `dst + n` otherwise.

It matches the strncpy-style padding semantics while returning the useful end pointer.
