# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/extent_tree.c

## Purpose

`extent_tree.c` manages pNFS blocklayout extents in red-black trees. It stores read-only and read-write layout extents, performs overlap insertion/removal/splitting/merging, tracks written invalid extents, and encodes layoutcommit updates for block and SCSI layouts.

## Main Responsibilities

- Maintain two extent trees in `struct pnfs_block_layout`: read-only (`bl_ext_ro`) and read-write (`bl_ext_rw`).
- Insert extents while trimming or splitting overlaps against existing ranges.
- Remove ranges from one or both trees, splitting extents when removal cuts through the middle.
- Lookup the extent covering a file-sector offset, preferring read-only extents for non-write lookups and falling back to read-write extents.
- Mark written ranges by converting matching invalid extents from unwritten to written state and removing conflicting COW/hole extents.
- Encode written extents into NFS layoutcommit layoutupdate buffers.
- Transition committing extents to committed read-write data on success or back to written on failure.

## Key Functions

- `ext_tree_insert()` chooses the target tree based on `be_state`, resolves overlaps, splits new extents when needed, and merges adjacent compatible extents.
- `ext_tree_remove()` removes a `[start, end)` sector range from read-only extents and optionally read-write extents.
- `ext_tree_lookup()` copies the matching extent into caller storage under `bl_ext_lock`.
- `ext_tree_mark_written()` removes read-only COW/hole coverage for a written range and marks matching untagged `PNFS_BLOCK_INVALID_DATA` extents as `EXTENT_WRITTEN`.
- `ext_tree_prepare_commit()` allocates a layoutupdate buffer, first trying a single page, then falling back to a vmalloc buffer sized by server `wsize` if needed.
- `ext_tree_try_encode_commit()` is all-or-nothing for a single-page buffer.
- `ext_tree_encode_commit()` encodes as many written extents as fit in the larger buffer and returns `-ENOSPC` when more layoutcommit work remains.
- `ext_tree_mark_committed()` frees commit buffers and updates extent state after the server replies.

## Data Structures and Invariants

Extents are ordered by `be_f_offset` and treated as half-open ranges ending at `be_f_offset + be_length`. Merge compatibility requires equal state, equal device pointer, adjacency in file offsets, contiguous volume offsets for data-bearing extents, and equal tags for invalid-data extents. `PNFS_BLOCK_NONE_DATA` extents do not require contiguous `be_v_offset`.

Device-id references are owned by extents. When extents are removed, merged away, or discarded, the code calls `nfs4_put_deviceid_node()`. When extents are split or duplicated, it increments the device-id reference with `nfs4_get_deviceid()`.

## Control Flow and State

The file uses `bl->bl_ext_lock` to serialize all rbtree mutation and lookup. Removal can detach multiple extents into a temporary list so expensive reference dropping and freeing occur after releasing the spinlock. Mark-written first removes read-only coverage in the affected range, then walks read-write invalid extents and splits/merges them to isolate the written subranges.

Layoutcommit encoding scans `bl_ext_rw` for `PNFS_BLOCK_INVALID_DATA` extents tagged `EXTENT_WRITTEN`. Encoded extents are retagged `EXTENT_COMMITTING`, and `bl_lwb` is converted into `lastbytewritten`. On commit success, committing extents become `PNFS_BLOCK_READWRITE_DATA`; on failure they return to `EXTENT_WRITTEN` for retry.

## Integration Points

- Uses `BLK_LO2EXT(NFS_I(inode)->layout)` to retrieve the blocklayout extension for layoutcommit.
- Encodes either pNFS block extents with device IDs or SCSI layout ranges depending on `bl_scsi_layout`.
- Uses `nfs4_layoutcommit_args` fields `layoutupdate_page`, `layoutupdate_pages`, `layoutupdate_len`, `start_p`, and `lastbytewritten`.
- Emits `trace_bl_ext_tree_prepare_commit()` for commit preparation.

## Risks and Edge Cases

- Several split/remove paths allocate with `GFP_ATOMIC` under a spinlock; memory pressure can produce `-ENOMEM`.
- `ext_tree_encode_commit()` uses `be_prev` when a buffer fills; the function relies on at least one extent having been encoded before the `-ENOSPC` path.
- The code uses `BUG()` if insertion sees an impossible overlap in `__ext_tree_insert()`, so callers must maintain non-overlap preconditions before raw insertion.
- Layoutcommit partial encoding intentionally commits a prefix and leaves remaining written extents for later commits.
- Sector-to-byte conversion shifts by `SECTOR_SHIFT`; callers must pass sector units consistently.

## Testing Focus

Coverage should include insertion around existing extents, middle removals that create two fragments, adjacent merge eligibility, invalid-data write marking with left/right splits, read-only versus read-write lookup ordering, single-page commit success, vmalloc fallback, partial commit `-ENOSPC`, and commit failure retry behavior.
