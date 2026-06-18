# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/merge.c

Implements `mergesort()` and `mergesort_r()` as a stable hybrid merge sort. The algorithm uses an auxiliary buffer, a pointer-threaded run list, insertion sort for tiny tails, and a natural/pairwise first pass followed by exponential/linear merge searches.

It rejects element sizes too small to hold internal list pointers with `EINVAL`, returns `-1` on allocation failure, and supports cookie-aware comparators via `mergesort_r()`. The public `mergesort()` adapts a normal two-argument comparator through a cookie wrapper.
