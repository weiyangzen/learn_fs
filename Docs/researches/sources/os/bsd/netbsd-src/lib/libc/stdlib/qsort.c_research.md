# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qsort.c

Implements `qsort()` and `qsort_r()` using Bentley and McIlroy’s tuned quicksort. It uses insertion sort for small partitions, median-of-three and pseudomedian-of-nine pivot selection, equal-key partitioning, word-sized swaps when alignment permits, and tail-recursion elimination.

`qsort_r()` is the core cookie-aware implementation; `qsort()` adapts a standard comparator through a cookie wrapper. The implementation asserts valid arguments but otherwise leaves comparator correctness to the caller.
