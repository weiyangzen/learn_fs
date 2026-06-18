# File Research: sources/local-fs/xfsdump/inventory/inv_idx.c

Implements per-filesystem inventory index files. Each `.InvIndex` contains a counter plus `invt_entry_t` records, where each record names a `.StObj` and its covered time range.

Key functions:
- `idx_create()` creates a new `.InvIndex` and its first storage object.
- `idx_create_entry()` appends a new storage-object entry and returns a token/descriptor for it.
- `idx_get_stobj()` opens the storage object referenced by the last index entry.
- `idx_put_sesstime()` updates an index entry’s start/end time when a session starts or ends.
- `idx_find_stobj()` and `idx_insert_newentry()` select a storage object for reconstruction by session time.
- `idx_put_newentry()` inserts a new index entry after the current index position during storage-object splitting.
- Debug helpers print index entries and display sessions.

Important dependencies:
- Calls `stobj_create()` and `stobj_makefname()` to allocate storage objects.
- Relies on `invt_idxinfo_t` during reconstruction and split operations.
- Uses `IDX_HDR_OFFSET()` to address index entries after the counter.

Notable observations:
- Several insertion branches that would create new in-between entries are commented out; current behavior often reuses an adjacent existing stobj.
- `idx_insert_newentry()` asserts unreachable if no placement is found.
- The index model assumes non-overlapping time periods and that the last entry is the writable target for normal dumping.
