# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcslen.c

Implements `wcslen()`. It advances a pointer until the terminating wide NUL and returns the pointer difference.

There is no special vectorization or bounds checking.
