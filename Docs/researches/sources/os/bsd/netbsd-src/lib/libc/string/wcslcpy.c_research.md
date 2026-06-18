# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslcpy.c

Implements `wcslcpy(dst, src, siz)`, the wide-character analogue of `strlcpy()`. It copies at most `siz - 1` wide characters, NUL-terminates when `siz != 0`, scans the rest of `src` on truncation, and returns the full source length.

The return value can be used to detect truncation.
