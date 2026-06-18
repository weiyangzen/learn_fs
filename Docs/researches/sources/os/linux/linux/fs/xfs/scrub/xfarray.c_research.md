# File Research: sources/os/linux/linux/fs/xfs/scrub/xfarray.c

This file implements `xfarray`, a sparse, xfile-backed array of fixed-size records for online repair. It stores large in-memory working sets in shmem-backed `xfile` storage so they can be paged out, and provides load/store/unset/append/iteration plus an xfile-aware sorting implementation.

Core data model:
- `struct xfarray` owns an `xfile`, record count `nr`, capacity `max_nr`, sparse zero-slot count `unset_slots`, object size, and optional log2 object-size optimization.
- All-zero records represent unset sparse entries and are skipped by iteration.
- Callers provide concurrency control.

Basic API:
- `xfarray_create`: creates backing xfile, validates capacity, computes max record count, and allocates scratch space after the struct.
- `xfarray_destroy`: destroys backing xfile and frees the array.
- `xfarray_load`: loads an element or returns `-ENODATA` beyond current length.
- `xfarray_store`: stores a nonzero element, extends `nr`, and rejects indexes beyond `max_nr`.
- `xfarray_unset`: truncates if unsetting the tail element, otherwise writes a zero record and increments `unset_slots`.
- `xfarray_store_anywhere`: reuses an unset slot if available, otherwise appends.
- `xfarray_load_next`: iterates to the next nonzero record, using `SEEK_DATA` to avoid instantiating sparse holes.
- `xfarray_bytes`: reports backing xfile memory usage.
- `xfarray_truncate`: discards backing storage and resets length.

Offset/index helpers:
- `xfarray_idx`: converts xfile byte offset to array index, using shift when object size is power-of-two.
- `xfarray_pos`: converts index to byte offset.
- `xfarray_scratch`: returns inline scratch buffer after the `xfarray` struct.

Sorting:
- `xfarray_sort` sorts array records with a custom nonrecursive quicksort plus optimizations:
  - Uses explicit index stacks instead of recursion.
  - Chooses pivots by median-of-nine sampling.
  - Processes smaller partitions first to cap stack depth.
  - Uses in-memory heapsort for small ranges.
  - Sorts directly in one backing folio when a range fits.
  - Caches folios during partition scans to reduce load/store overhead.
- `xfarray_sortinfo_alloc` builds the stack and scratch area.
- `xfarray_isort`, `xfarray_foliosort`, `xfarray_qsort_pivot`, `xfarray_qsort_push`, and `xfarray_sort_scan` implement the optimized sort.
- Debug builds count loads, stores, compares, and heapsorts.

Risk notes:
- Stored records must not be all zero, because zero means unset.
- Sorting assumes array contents are valid records; sparse/unset handling is mostly in pivot sampling and iteration paths.
- `xfarray_sort` rejects arrays with `>= 2^63` records.
- Large sorts can be interrupted through `xchk_maybe_relax` behavior controlled by sort flags.
- Any xfile load/store/folio error aborts the sort and returns the error.
