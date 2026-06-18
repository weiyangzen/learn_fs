# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsstr.c

Implements `wcsstr()` and, when compiled with `WCSWCS`, `wcswcs()`. It handles an empty needle by returning the haystack, rejects needles longer than the haystack, then performs a straightforward nested substring search.

This is a simple O(n*m) wide substring implementation.
