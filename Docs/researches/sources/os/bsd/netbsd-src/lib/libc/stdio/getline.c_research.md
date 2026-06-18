# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getline.c

Implements `getline()` as a direct call to `getdelim(buf, buflen, '\n', fp)`. It contains no independent line-reading logic.

The weak alias maps `getline` to `_getline` where supported.
