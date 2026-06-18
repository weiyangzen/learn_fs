# sources/test-tools/stress-ng/stress-radixsort.c research

Purpose: implements `radixsort`, a CPU/cache/memory sort stressor for arrays of short random strings, using libc/BSD `radixsort` when available or a local stable counting-radix implementation.

Important APIs, types, and functions: `radixsort_func_t` abstracts the sort signature. `radix_count_sort()` performs a per-digit stable counting pass over 257 buckets. `radixsort_nonlibc()` computes string lengths and sorts from the last character to the first. `stress_radixsort_methods` exposes method selection; a reverse lookup table enables reverse ordering.

Control flow: `stress_radixsort()` selects method and size, allocates one contiguous text slab and a pointer array, installs optional `SIGALRM` longjmp recovery, initializes random fixed-size strings once, synchronizes, then repeatedly sorts forward, optionally verifies ascending order, sorts reverse with `revtable`, optionally verifies descending order, randomizes the first character of every string, and increments bogo ops.

State and persistence: all text and pointer data are heap allocations freed at exit. Signal jump state is process-global but restored. No files persist.

Dependencies and integration: depends on stress-ng random string generation, CPU cache helpers, signal wrappers, and optional BSD/libc radixsort. It is classified as CPU/cache/memory/sort and `VERIFY_OPTIONAL`.

Risks: local implementation uses `unsigned short` lengths, safe for 8-byte strings but not general-purpose long strings. Verification uses `strcmp`, so reverse-table sort must align with lexical expectations. Longjmp interruption must restore handlers and free allocations through the tidy path.

Test signals: method log, optional ordering failure messages, bogo progress, and clean fallback to nonlibc implementation where libc radixsort is unavailable.
