# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslcat.c

Implements `wcslcat(dst, src, siz)`, the wide-character analogue of `strlcat()`. It finds the end of `dst` within `siz`, appends as much of `src` as fits while NUL-terminating when possible, and returns the length it tried to build.

A return value >= `siz` indicates truncation.
