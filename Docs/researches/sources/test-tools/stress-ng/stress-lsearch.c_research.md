# sources/test-tools/stress-ng/stress-lsearch.c

Purpose: implements `lsearch`, a CPU/cache/memory/search stressor for linear search and insertion. It compares libc `lsearch`/`lfind` with local non-libc and sentinel implementations.

Important APIs/types/functions: function pointer typedefs abstract `lfind` and `lsearch`. `lfind_nonlibc()` walks elements linearly; `lsearch_nonlibc()` appends absent keys. `lfind_sentinel()` temporarily copies the key into the last slot to avoid an end check, then restores it. `stress_lsearch_cmp_int32()` increments the global sort-compare counter. `stress_lsearch()` configures size/method, allocates arrays, shuffles input, inserts, searches, verifies optional correctness, and emits metrics.

Control flow: each iteration shuffles source data, populates the root array through the chosen implementation, resets comparison counters, times `lfind` over inserted elements, optionally verifies returned pointers/values, accumulates comparison count and item count, and increments bogo operations.

State and persistence: state is heap-allocated arrays for the run plus global sort comparison counters. No external state persists. Metrics report comparisons per second and comparisons per item.

Dependencies/integration: uses optional `<search.h>`, stress-ng sort helpers, method option lookup, maximize/minimize sizing, bogo counters, and optional verification.

Risks/test signals: the sentinel implementation mutates the final element while searching; restoration must be correct. Large sizes produce O(n^2) work. Useful signals are allocation/skip behavior, method enumeration, optional verification without missing elements, and comparison metrics.
