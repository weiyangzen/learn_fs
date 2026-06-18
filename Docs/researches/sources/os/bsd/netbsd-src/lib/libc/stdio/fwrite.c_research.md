# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwrite.c

Implements `fwrite()` by wrapping the caller buffer in a single `__siov`/`__suio` vector and passing it to `__sfvwrite()` under `FLOCKFILE()`. It returns the requested object count on complete success or the number of whole objects actually written after a short/error write.

Important behavior: it detects `size * count` overflow before writing, sets `errno = EOVERFLOW`, marks `__SERR`, and returns zero. Zero size or zero count returns zero as required by SUSv2.
