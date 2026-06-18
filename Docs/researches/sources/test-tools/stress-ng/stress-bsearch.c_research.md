<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bsearch.c -->
# sources/test-tools/stress-ng/stress-bsearch.c

Purpose: `stress-bsearch.c` implements the `bsearch` CPU/cache/memory search stressor. It searches every element in a sorted 32-bit integer array using libc binary search, an internal binary search, or a ternary-search variant.

Important APIs/types/functions: `bsearch_func_t` abstracts libc-compatible search functions. `bsearch_nonlibc()` is a standard lower/upper binary search. `bsearch_ternary()` probes two midpoints and narrows thirds. `stress_bsearch_methods[]` conditionally includes libc `bsearch`, plus nonlibc and ternary implementations. `stress_bsearch()` owns allocation, repeated search, verification, and metrics.

Control flow: the stressor resolves `bsearch-method` and `bsearch-size`, rounds allocation up to a multiple of 8 elements, mmaps the data array, syncs, then loops. Each iteration initializes sorted data, resets sort comparison counters, searches for every element with the selected method and `stress_sort_cmp_fwd_int32`, optionally verifies the returned pointer/value, records duration and comparison count, and increments bogo operations.

State and persistence behavior: state is an anonymous mapped array and comparison counters managed by `core-sort`. No files or persistent kernel resources are used.

Dependencies and integration points: depends on optional `<search.h>`/`bsearch`, stress-ng mmap helpers, core sort initialization/comparison helpers, option method selection, process states, sync barriers, and metrics. It is `VERIFY_OPTIONAL`.

Risks: `bsearch_ternary()` uses `while (upper >= lower)` with unsigned `size_t`; if `mid1` is zero and `cmp1 < 0`, `upper = mid1 - 1` underflows. Sorted input and exact-key searches reduce exposure, but missing-key tests would be risky. Method names in help mention only two methods while the table includes `ternary`.

Test signals: run every method, minimum/default/maximum sizes, verify mode, and missing-key unit coverage for `bsearch_ternary()` if isolated. Metrics are `bsearch comparisons per sec` and `bsearch comparisons per item`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bsearch.c -->
