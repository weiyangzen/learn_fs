# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/bsearch.c

Read completely: 85 lines.

Implements `bsearch()`. It performs an iterative binary search over fixed-width elements, comparing the key with the middle element, returning a writable pointer to the matched element via `__UNCONST`, or `NULL` when absent.

The loop adjusts `base` and `lim` carefully for odd/even counts after moving right. Preconditions are asserted for key, comparator, and non-null base unless `nmemb == 0`.
