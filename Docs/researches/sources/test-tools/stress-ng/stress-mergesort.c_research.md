# sources/test-tools/stress-ng/stress-mergesort.c

Purpose: `stress-mergesort.c` implements a CPU/cache/memory sort stressor over random 32-bit integers. It can use a platform libc/BSD `mergesort` when available or an internal non-libc merge sort implementation, and it optionally verifies sorted ordering under global verify mode.

Important APIs/types/functions: `mergesort_func_t` abstracts sort implementations. `stress_mergesort_method_t` backs the method option. `mergesort_copy4`, `mergesort_copy`, `mergesort_partition4`, and `mergesort_partition` implement the internal merge sort with a 4-byte optimized path. `mergesort_nonlibc` allocates a temporary left/right workspace with `stress_mmap_populate`. `stress_mergesort_handler` uses siglongjmp on platforms where SIGALRM interruption is supported.

Control flow: `stress_mergesort` selects the method, resolves `--mergesort-size` with minimize/maximize overrides, maps the data array, installs the SIGALRM jump handler, initializes sorted data, synchronizes, and loops. Each iteration shuffles data, forward sorts and optionally verifies ascending order, reverse sorts and optionally verifies descending order, mangles data, reverse sorts again, then increments the bogo counter. Metrics record comparisons per second and comparisons per item from `stress_sort_compare_get`.

State and persistence behavior: all data is anonymous memory (`mergesort-data` plus temporary workspace); no persistent state is written. Sort comparison counters are shared through stress-ng sort helpers for the current process. SIGALRM state is restored on normal and jump-based exit.

Dependencies and integration points: the stressor uses `core-sort`, `core-mmap`, `core-madvise`, `core-signal`, target clones, and stress-ng memory/metric helpers. It registers `stress_mergesort_info` with classifiers `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SORT | CLASS_HOT`, verify mode `VERIFY_OPTIONAL`, and options for method and size.

Risks: the recursive merge implementation can consume stack proportional to `log(n)` but temporary mmap size is `nmemb * size`; allocation failure returns a sort failure and is surfaced. Incorrect size handling in the generic partition path would corrupt memory. SIGALRM longjmp must not bypass cleanup. Verification only runs when global verify is enabled, so performance runs can hide ordering bugs until verify tests are used.

Test signals: run `stress-ng --mergesort 1 --mergesort-ops 1 --verify`, test `--mergesort-method mergesort-nonlibc`, test libc method on systems where present, and exercise `--mergesort-size` at min/default/max boundaries. Metrics should be nonzero for completed iterations.
