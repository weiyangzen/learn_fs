# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncat.c

Implements `wcsncat()`. It appends at most `n` wide characters from source to the end of destination, writes a terminating NUL, and returns the original destination pointer.

The destination must have enough room.
