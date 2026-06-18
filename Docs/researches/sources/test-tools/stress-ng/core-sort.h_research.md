# sources/test-tools/stress-ng/core-sort.h

Purpose: declares sort helpers and defines inline comparator functions used by stressors and the fallback quicksort.

Important APIs/types/functions: swap/copy function pointer typedefs, data init/shuffle/mangle functions, comparison counter accessors, `stress_sort_swap_func`, `stress_sort_copy_func`, `qsort_bm`, `shim_qsort`, string comparator, and generated forward/reverse comparators for int8/int16/int32/int64/int.

Control flow: if libc `qsort` exists, `shim_qsort` calls it; otherwise it calls `qsort_bm`. Comparator macros load typed values, increment `stress_sort_compares`, and return conventional -1/0/1 ordering, with separate reverse variants.

State and persistence: comparators mutate global `stress_sort_compares`; no other state.

Dependencies/integration: includes inttypes and attributes; relies on `strcmp` and the `stress_sort_compares` definition in `core-sort.c`. Used broadly by sort stressors and settings display sorting.

Risks: comparator typed loads require correctly typed/aligned array elements. The compare counter creates global side effects and is not thread-safe.

Test signals: comparator ordering for equal/less/greater values, reverse ordering, string sorting, and shim selection with/without `HAVE_QSORT`.
