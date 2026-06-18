<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bubblesort.c -->
# sources/test-tools/stress-ng/stress-bubblesort.c

Purpose: `stress-bubblesort.c` implements the `bubblesort` CPU/cache/memory/hot sort stressor. It sorts 32-bit integer arrays using either an optimized bubble-sort pass or a naive swapped-loop implementation.

Important APIs/types/functions: `bubblesort_func_t` abstracts qsort-like sort functions. `bubblesort_fast()` tracks the last swap position and shortens the next pass. `bubblesort_naive()` performs full passes until no swaps occur. Both use `stress_sort_swap_func(size)` and the comparator supplied by `core-sort`. `stress_bubblesort_methods[]` exposes `bubblesort-fast` and `bubblesort-naive`; `stress_bubblesort()` handles option parsing, allocation, sorting, verification, and metrics.

Control flow: the stressor selects method and size, mmaps a 32-bit integer array, optionally installs a `SIGALRM` longjmp handler, initializes data, syncs, then loops. Each iteration shuffles data, sorts ascending and optionally verifies, sorts descending and verifies, mangles data, reverse-sorts again and verifies, and increments bogo operations. Comparison counts are collected through `stress_sort_compare_get()`.

State and persistence behavior: no persistent state is created. Runtime state is the anonymous mapping, selected method, optional jump state, comparison/duration counters, and process signal disposition. The mapping is named `bubblesort-data` and may be advised for collapse.

Dependencies and integration points: integrates with stress-ng mmap/madvise, signal wrappers, core sort helpers, option method selection, process states, sync barriers, and metrics. It registers `VERIFY_OPTIONAL` and classifier bits including `CLASS_HOT`.

Risks: bubble sort is intentionally expensive; maximum sizes can produce long iterations, making the `SIGALRM` escape path important. The help string for `bubblesort-method` appears to miss a closing bracket in the user-facing text. Longjmp paths must restore the prior alarm handler before cleanup.

Test signals: run both methods, verify mode, small/default/maximum sizes, forced alarm/timeout behavior, and mmap failure skip paths. Metrics are `bubblesort comparisons per sec` and `bubblesort comparisons per item`; order failures identify ascending or reverse sort errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bubblesort.c -->
