# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lsearch.c

Read completely: 107 lines.

Implements `lsearch()` and `lfind()` through shared `linear_base()`. Both linearly scan fixed-width array elements with the caller comparator; `lfind()` returns the matching element or `NULL`, while `lsearch()` appends the key bytes at the end and increments `*nelp` when absent.

The implementation cannot verify caller-provided array capacity, and the source comments explicitly note that historical documentation's “not enough room” error cannot be implemented with this API.
