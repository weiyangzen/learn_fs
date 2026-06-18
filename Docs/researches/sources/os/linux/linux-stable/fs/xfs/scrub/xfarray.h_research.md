# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.h

Declares the xfile-backed fixed-record array API and sort state.

Key elements:
- `xfarray_idx_t` is a 64-bit array index type.
- Defines `XFARRAY_NULLIDX`, `XFARRAY_CURSOR_INIT`, and `foreach_xfarray_idx`.
- `struct xfarray` stores the backing xfile, current element count, maximum element count, unset slot count, object size, and optional object-size log2.
- Public operations cover create/destroy, load, sparse load, unset, store, append, store-anywhere, null-record testing, length, non-null iteration, bytes used, truncation, and sorting.
- `xfarray_iter` wraps `xfarray_load_next` into a 1/0/negative iteration API.
- Sort definitions include `xfarray_cmp_fn`, small-sort threshold, median-of-nine pivot count, and `struct xfarray_sortinfo`.
- `struct xfarray_sortinfo` documents its variable trailing allocation layout for quicksort stacks and scratch/pivot storage.
- `XFARRAY_SORT_KILLABLE` is the public sort flag.
