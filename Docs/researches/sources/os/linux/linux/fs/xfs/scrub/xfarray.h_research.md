# File Research: sources/os/linux/linux/fs/xfs/scrub/xfarray.h

This header declares the xfile-backed fixed-size array API and sort support.

Key definitions:
- `xfarray_idx_t`: 64-bit array index type.
- `XFARRAY_NULLIDX`: invalid index sentinel.
- `XFARRAY_CURSOR_INIT`: initial iterator cursor.
- `foreach_xfarray_idx`: simple full-index iteration macro.

Key type:
- `struct xfarray`: backing `xfile`, current length, max length, unset-slot count, object size, and object-size log2 cache.

Basic functions:
- Lifecycle: `xfarray_create`, `xfarray_destroy`.
- Element operations: `xfarray_load`, `xfarray_load_sparse`, `xfarray_store`, `xfarray_unset`, `xfarray_append`, `xfarray_store_anywhere`.
- Iteration: `xfarray_length`, `xfarray_load_next`, `xfarray_iter`.
- Utility: `xfarray_element_is_null`, `xfarray_truncate`, `xfarray_bytes`.

Sort declarations:
- `xfarray_cmp_fn`: comparator type.
- `XFARRAY_ISORT_SHIFT`, `XFARRAY_ISORT_NR`: small-range sort thresholds.
- `XFARRAY_QSORT_PIVOT_NR`: median-of-nine pivot sample count.
- `struct xfarray_sortinfo`: state for xfile-backed quicksort, including stack depth, flags, relax state, cached folio, and debug counters.
- `XFARRAY_SORT_KILLABLE`: sort can be interrupted by fatal signal.
- `xfarray_sort`: public sort entry point.

Risk notes:
- The sortinfo structure uses extra bytes after the struct for variable-size stacks and scratch records; the header documents the implied layout because C cannot express multiple VLAs in a struct.
- `xfarray_load_sparse` treats `-ENODATA` as an all-zero record for callers that want sparse semantics.
