# File Research: sources/local-fs/xfsprogs/repair/da_util.c

## Purpose

`da_util.c` provides shared helpers for repairing XFS directory and attribute DA btrees. It reads possibly non-contiguous DA blocks, traverses interior nodes, maintains a cursor path, verifies parent-child hash propagation, checks sibling pointers, and releases dirty buffers.

## Main Functions

- `da_read_buf` reads one logical DA block from one or more mapped filesystem extents.
- `traverse_int_dablock` walks from the DA root down the left side of the tree and initializes a cursor.
- `release_da_cursor` releases held interior-node buffers in normal paths.
- `err_release_da_cursor` releases held buffers in error paths.
- `verify_da_path` validates and advances parent cursor state when a lower-level traversal crosses a block boundary.
- `verify_final_da_path` validates the final right edge of the tree after all leaves are processed.

## DA Tree Model

Directory and attribute DA interior nodes store `<hashval, before>` entries. Unlike many btrees, the propagated key is the greatest hash value in the child block. The cursor stores, for each level, the current block buffer, file block number, last verified hash value, current entry index, and dirty flag.

## Buffer Handling

`da_read_buf` builds an `xfs_buf_map` array from repair `bmap_ext_t` records. It uses a small stack array for up to four mappings and allocates only for rare multi-extent blocks. Reads use salvage mode and caller-supplied buffer ops.

## Validation Behavior

`traverse_int_dablock` verifies magic values, node levels, node entry counts, and root-to-leaf level consistency. For directories, it handles the special case where the root is a `LEAFN`.

`verify_da_path` checks that the parent entry points to the just-processed child block and that the parent hash matches the child’s greatest hash. If the parent block is exhausted, it validates that block upward, reads the next sibling, checks sibling back pointer/magic/count/level, and updates the cursor.

`verify_final_da_path` checks the rightmost path, including used/count consistency, final forward pointer, child block pointer, and final hash value.

## Repair Behavior

If a parent hash value is stale but the structure is otherwise consistent, the helper updates it in modify mode and marks the buffer dirty. If a buffer had a bad checksum but otherwise validates, it marks the block dirty to force checksum recomputation.

## Important Invariants

- Cursor `active` is the highest tree level.
- Interior node levels must descend by exactly one from root to leaves.
- Parent entries must point to the child file block just processed.
- Parent hash values must equal the child’s greatest hash.
- Rightmost interior blocks must have `forw == 0`.
- Dirty buffers are only written in modify mode.

## Repair and Risk Notes

This code is central to both directory and attribute repair. Its most subtle invariant is that cursor indices often point to the next unprocessed entry, while hash values refer to the last processed child. Mismanaging that off-by-one convention can invalidate the whole path check.
