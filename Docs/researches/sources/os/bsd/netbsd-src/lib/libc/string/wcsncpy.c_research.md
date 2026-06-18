# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncpy.c

Implements `wcsncpy()`. It copies up to `n` wide characters from source and pads the destination with wide NULs if the source ends early.

It returns the original destination pointer and does not guarantee NUL termination when the source length is at least `n`.
