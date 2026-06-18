# File Research: sources/os/linux/linux/fs/nfs/blocklayout/extent_tree.c

## Purpose
Manages pNFS block layout extent state in red-black trees. It tracks read-only and read/write extents, performs insertion/removal/splitting/merging, marks written extents, and encodes layoutcommit updates back to the NFS server.

## Main Responsibilities
- Store block extents in two interval-like rbtrees: read-only and read/write.
- Merge adjacent compatible extents.
- Remove or split extents over recalled or overwritten ranges.
- Look up extents for I/O mapping.
- Track invalid extents that have been written and need layoutcommit.
- Encode block or SCSI layoutcommit updates into XDR buffers.
- Update extent state after layoutcommit succeeds or fails.

## Key Functions
- `ext_tree_insert()` inserts a new extent into the correct tree, trimming or splitting around overlaps.
- `ext_tree_lookup()` finds an extent covering a sector, preferring read-only only when `rw` is false, then checking read/write extents.
- `ext_tree_remove()` removes a range from read-only and optionally read/write trees.
- `ext_tree_mark_written()` removes conflicting COW/hole ranges and marks written invalid extents as `EXTENT_WRITTEN`.
- `ext_tree_prepare_commit()` allocates layoutupdate storage and encodes all or as many written extents as fit.
- `ext_tree_mark_committed()` converts committing invalid extents to read/write extents on success or back to written on failure.
- Internal helpers handle rbtree search, insert, remove, split, and left/right merge.

## Control Flow
Extent insertion chooses `bl_ext_rw` for `READWRITE_DATA` and `INVALID_DATA`, and `bl_ext_ro` for `READ_DATA` and `NONE_DATA`. It searches for overlap under `bl_ext_lock`, inserts directly when no overlap exists, drops fully covered extents, trims partially covered extents, or duplicates/splits new extents as necessary.

Layoutcommit preparation first tries a single page. If that cannot fit all written extents, it allocates a larger vmalloc buffer sized to the server write size and encodes a partial set if still necessary.

## Data and Ownership
- Each `pnfs_block_extent` owns a reference to its `be_device`.
- Merging or deleting extents releases device references with `nfs4_put_deviceid_node()`.
- Removed extents are staged on a temporary list while under spinlock, then freed after unlock.
- Commit data may use a single page or a vmalloc-backed page array; `ext_tree_free_commitdata()` frees either representation.

## Locking
`bl->bl_ext_lock` protects both extent trees and `bl_lwb`. Allocation inside locked paths uses `GFP_ATOMIC` where needed. Freeing removed extents is deferred until after the spinlock is released.

## Encoding Behavior
- Block layouts encode deviceid, file offset, length, zero storage offset, and `PNFS_BLOCK_READWRITE_DATA`.
- SCSI layouts encode only offset and length ranges.
- `lastbytewritten` is `bl_lwb - 1` when all pending extents fit; for partial commits it is the last byte covered by the last encoded extent.

## Notable Details
- `PNFS_BLOCK_NONE_DATA` extents can merge without virtual-offset continuity.
- `PNFS_BLOCK_INVALID_DATA` extents also require matching `be_tag` to merge.
- `ext_tree_mark_written()` only marks invalid extents with tag `0`; already tagged extents are skipped.
- On layoutcommit failure, committing extents return to `EXTENT_WRITTEN` for retry.

## Risks and Edge Cases
- `ext_tree_encode_commit()` uses `be_prev` when the buffer fills; this assumes at least one extent was encoded before `-ENOSPC`.
- Some error paths convert allocation failure to `-EINVAL` in `ext_tree_insert()` split handling.
- The rbtree implementation assumes non-overlap invariants; unexpected overlap in raw insert triggers `BUG()`.
- Sector-to-byte shifts must remain consistent with protocol sizes.

## Integration Points
This file backs pNFS block layout I/O, recall handling, and `LAYOUTCOMMIT`. It depends on `blocklayout.h` structures and NFS layoutcommit argument structures from core NFSv4 code.
