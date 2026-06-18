# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsrchr.c

Implements `wcsrchr()`. It first walks to the terminating NUL, then scans backward until the start of the string looking for the requested wide character.

Searching for NUL returns the terminator pointer.
