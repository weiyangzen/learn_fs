# File Research: sources/os/linux/linux-stable/fs/ntfs3/index.c

## Role

Implements NTFS index trees. NTFS directories and metadata indexes are stored as resident `INDEX_ROOT` entries plus optional nonresident `INDEX_ALLOCATION` buffers tracked by `BITMAP` attributes. This file provides collation, index bitmap scanning, node I/O, B+tree search/enumeration, insertion with splitting, deletion with collapse/shrink, and duplicate metadata updates.

## Key Functions

- `cmp_fnames()`, `cmp_uint()`, `cmp_sdh()`, and `cmp_uints()` implement supported NTFS collation rules for filenames, integer IDs, security hashes, object IDs, and reparse keys.
- `get_cmp_func()` maps an `INDEX_ROOT` type/rule pair to the comparison callback.
- `bmp_buf_get()` and `bmp_buf_put()` read or map resident/nonresident index bitmaps, zeroing invalid tails and extending valid size as needed.
- `indx_mark_used()` and `indx_mark_free()` update allocation bitmap bits for index buffers.
- `scan_nres_bitmap()` scans nonresident bitmap blocks using the cached run tree, loading runs on demand under `indx->run_lock`.
- `indx_find_free()` and `indx_used_bit()` find free or used index-buffer bits.
- `hdr_find_split()` chooses a split point near the middle of an index header.
- `hdr_insert_head()`, `hdr_find_e()`, `hdr_insert_de()`, and `hdr_delete_de()` manipulate entries inside a single index header.
- `index_hdr_check()` and `index_buf_check()` validate index header sizes, fixup metadata, signatures, and VBNs.
- `fnd_clear()`, `fnd_push()`, `fnd_pop()`, and `fnd_is_empty()` manage `ntfs_fnd`, the search-path cache for tree operations.
- `indx_init()` validates an index root and derives index-buffer sizing and VBN conversion shifts.
- `indx_new()` creates and initializes a new on-disk index allocation buffer.
- `indx_get_root()` locates and validates the resident root attribute.
- `indx_read_ra()` reads an index buffer, fixes update-sequence arrays if needed, validates the buffer, and loads missing allocation runs on demand.
- `indx_find()` searches a sorted NTFS index tree and stores the path in `ntfs_fnd`.
- `indx_find_sort()` iterates entries in sorted order.
- `indx_find_raw()` enumerates raw entries across root and allocation buffers, used by metadata scans.
- `indx_create_allocate()` creates initial `INDEX_ALLOCATION` and `BITMAP` attributes.
- `indx_add_allocate()` grows or reuses index allocation space and bitmap bits.
- `indx_insert_into_root()` inserts into the resident root or promotes root entries into a new external buffer.
- `indx_insert_into_buffer()` inserts into an allocation buffer and recursively promotes split entries upward.
- `indx_insert_entry()` is the public insertion API.
- `indx_delete_entry()` removes an entry, handles replacement entries, frees empty branches, shrinks allocation, and collapses a tree back to an empty resident root when possible.
- `indx_update_dup()` updates duplicated file metadata inside a directory entry.

## Synchronization and State

- `indx->run_lock` protects `alloc_run` and `bitmap_run` against concurrent read/enumeration and lazy run loading.
- Caller-side inode locks protect structural modifications to the index attributes.
- `indx->version` increments on insert/delete to signal structural changes.

## Research Notes

The implementation treats the resident root as both tree root and possible leaf. When it grows too large, entries move to allocation buffers and the root becomes a parent pointer. Deletion is more complex than insertion because it may replace internal entries, free child buffers, shrink attributes, or collapse the entire tree back into a resident root.
