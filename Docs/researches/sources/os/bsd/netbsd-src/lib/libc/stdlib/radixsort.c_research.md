# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/radixsort.c

Implements BSD string-pointer radix sorting through `radixsort()` and `sradixsort()`. `radixsort()` uses an unstable in-place American-flag-style radix sort with a bounded stack; `sradixsort()` allocates temporary pointer storage and performs a stable variant.

The optional translation table maps byte values and validates the configured end character. Small buckets use insertion sort; larger buckets are partitioned by per-byte histograms and recursive stack entries.
