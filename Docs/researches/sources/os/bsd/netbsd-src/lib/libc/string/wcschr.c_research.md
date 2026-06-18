# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcschr.c

Implements `wcschr()`. It scans forward until it finds the requested wide character or reaches the terminating NUL.

Searching for NUL returns a pointer to the terminator.
