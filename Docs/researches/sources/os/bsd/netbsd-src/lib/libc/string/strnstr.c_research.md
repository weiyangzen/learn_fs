# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strnstr.c

Implements bounded substring search `strnstr(s, find, slen)`. It scans for the first needle character within `slen`, ensures the rest of the needle fits in the remaining bound, and verifies with `strncmp()`.

An empty needle returns the haystack pointer.
