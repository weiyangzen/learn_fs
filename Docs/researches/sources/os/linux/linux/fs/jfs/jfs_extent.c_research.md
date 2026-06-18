# File Research: sources/os/linux/linux/fs/jfs/jfs_extent.c

## Role

Implements regular-file extent allocation, allocation hints, and conversion of not-recorded extents to recorded extents.

## Key Responsibilities

- Allocates file extents in `extAlloc()`, validating read-write state, clamping length to `MAXXLEN`, deriving file offset from page number, and using previous extent hints when possible.
- Extends a previous adjacent extent through `xtExtend()` when the new allocation is physically contiguous and has the same recorded/not-recorded state.
- Inserts a new xtree extent through `xtInsert()` when extension is not possible.
- Uses `extBalloc()` to allocate contiguous block ranges, backing off request size by powers of two until at least one page worth of blocks can be allocated.
- Charges quota after block allocation and rolls back both block-map and quota allocation if xtree updates fail.
- Provides `extHint()` to return the extent covering the previous page, preserving only the `XAD_NOTRECORDED` flag.
- Provides `extRecord()` to update an extent from not-recorded to recorded through `xtUpdate()`.
- Tracks active allocation group for regular files in the primary fileset so block allocator active-AG accounting can reduce fragmentation.

## Important Interactions

- Uses `dbAlloc()`/`dbFree()` for block-map allocation and release.
- Uses xtree operations (`xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`) to record allocated extents in file metadata.
- Serializes extent updates with `txBeginAnon()` and `JFS_IP(ip)->commit_mutex`.
- Calls quota helpers for block charging and rollback.
- Calls `jfs_commit_inode()` when `COMMIT_Synclist` was set by anonymous transaction processing.

## Invariants and Risks

- Extent allocation refuses read-only filesystems via `isReadOnly()`.
- `extHint()` treats missing previous-page mappings as "no hint" rather than an error.
- A hinted previous extent must be exactly one page long in `extHint()`; otherwise the xtree is considered corrupt.
- `extBalloc()` never returns less than `nbperpage` blocks; inability to allocate one page returns `-ENOSPC`.
- Rollback paths must free both allocated blocks and quota reservations to avoid leaks.
