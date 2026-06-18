# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.c

Implements large fixed-size record arrays backed by an `xfile`.

Core model:
- Stores fixed-size records in a shmem-backed xfile so online repair can handle large transient datasets without pinning all memory.
- Records can be unset; unset slots are zeroed and skipped by iteration.
- Callers provide their own concurrency control.

Key behavior:
- `xfarray_create` creates the backing xfile, allocates the array plus scratch space, records object size/log2 optimization, computes max capacity from `MAX_LFS_FILESIZE`, and enforces optional required capacity.
- `xfarray_load`, `xfarray_store`, `xfarray_unset`, `xfarray_store_anywhere`, `xfarray_length`, `xfarray_bytes`, and `xfarray_truncate` provide basic array operations.
- `xfarray_find_data` uses `SEEK_DATA` carefully to skip sparse xfile holes without instantiating pages while iterating.
- `xfarray_load_next` returns the next non-zero record and advances the cursor.
- Sorting is a nonrecursive quicksort with an explicit index stack, median-of-nine pivot selection, smaller-partition-first stack use, small-partition heapsort, direct folio heapsort when possible, and folio caching during partition scans.
- `xfarray_sort` rejects arrays with at least `2^63` records, allocates sort scratch/stack state, runs quicksort/heapsort hybrids, supports termination checks, emits trace stats, and releases cached folios.

Important constraints:
- Object size must be smaller than a page.
- Fully zeroed records are treated as unset/sparse records.
- Sort termination is driven through `xchk_maybe_relax`; the `XFARRAY_SORT_KILLABLE` flag affects interruptibility setup.
