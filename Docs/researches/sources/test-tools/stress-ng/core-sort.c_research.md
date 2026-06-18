# sources/test-tools/stress-ng/core-sort.c

Purpose: supplies sort-related test data generation, swap/copy helpers, comparison counting, and a bundled Bentley-McIlroy quicksort fallback.

Important APIs/types/functions: `stress_sort_compare_reset/get` manage `stress_sort_compares`. `stress_sort_data_int32_init`, `shuffle`, and `mangle` create and perturb integer data. `stress_sort_swap_func` and `stress_sort_copy_func` choose optimized element-size helpers. `qsort_bm` implements fallback quicksort.

Control flow: data init generates monotonically increasing values using random deltas and an unrolled macro. Shuffle uses a linear congruential sequence and optimizes modulo with a bitmask for power-of-two lengths. Mangle flips high bits to reorder signed comparisons. Swap/copy dispatch returns exact-width helpers for 1/2/4/8 byte elements or byte loops otherwise. `qsort_bm` uses insertion sort below `THRESH`, median-of-three or pseudomedian pivoting for larger arrays, partitions equal elements to both ends, swaps equal partitions back to the center, and recursively sorts left/right partitions.

State and persistence: `stress_sort_compares` is a global aligned counter incremented by comparator functions in the header. Sorting mutates caller-provided arrays only.

Dependencies/integration: uses random generator `stress_mwc32`, pragma unroll macros, target clones, and header comparators. `shim_qsort` selects libc `qsort` or this fallback.

Risks: helper swap/copy functions assume suitable alignment for typed loads in exact-width variants. `stress_sort_data_int32_init` unroll macro assumes callers provide lengths compatible with the loop pattern used by stressors; arbitrary small non-multiple lengths would risk overrun. The global compare counter is not synchronized.

Test signals: sort correctness for many element sizes, duplicate-heavy arrays, small arrays under threshold, non-power-of-two shuffle, compare counter resets, and fallback builds without libc `qsort`.
