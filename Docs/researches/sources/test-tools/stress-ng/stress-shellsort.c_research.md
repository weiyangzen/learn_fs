# sources/test-tools/stress-ng/stress-shellsort.c

Purpose: implements the `shellsort` CPU/cache/memory stressor, repeatedly shell-sorting arrays of 32-bit integers in forward and reverse order and optionally verifying sort correctness.

Important APIs/types/functions: `shellsort32`, `stress_shellsort`, `stress_shellsort_handler`, `stress_sort_data_int32_init`, `stress_sort_data_int32_shuffle`, `stress_sort_data_int32_mangle`, `stress_sort_cmp_fwd_int32`, `stress_sort_cmp_rev_int32`, `stress_sort_compare_get`, `stress_mmap_populate`, `stress_madvise_collapse`, `sigsetjmp`, and `siglongjmp` helpers.

Control flow: the worker resolves `shellsort-size`, maps the integer array, installs a SIGALRM recovery handler when `siglongjmp` is available, initializes the data, synchronizes start, then repeats shuffle/forward-sort, optional verify, reverse-sort, optional verify, mangle, reverse-sort again, optional verify, and bogo increment. It records comparison counts and elapsed time across all sort passes.

State and persistence behavior: state is one private anonymous mapping named `shellsort-data`, sort comparison counters maintained by core sort helpers, and local duration/count totals. The signal jump path restores the old SIGALRM handler and frees the mapping.

Dependencies and integration points: registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SORT | CLASS_HOT`, optional verify, with `shellsort-size` option. It integrates with core sort helpers, mmap/madvise helpers, and stress-ng signal recovery.

Risks and test signals: verify-mode ordering failures indicate comparator or sort corruption. Other signals are mmap failure, handler restoration bugs, interruption during sort, and metric sanity for comparisons/sec and comparisons/item.
