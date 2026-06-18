# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsnlen.c

Implements `wcsnlen(s, maxlen)`. It scans at most `maxlen` wide characters or until a wide NUL and returns the number examined before termination.

This is the bounded wide-string length helper.
