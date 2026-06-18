# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscat.c

Implements `wcscat()`. It advances to the destination string’s terminating NUL, copies the source wide string, writes a final NUL, and returns the original destination pointer.

No bounds checking is performed.
