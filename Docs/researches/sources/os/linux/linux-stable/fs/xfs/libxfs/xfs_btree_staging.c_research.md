# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.c

## Role in the repository

`xfs_btree_staging.c` implements fake-root staging cursors and the generic bulk loader for constructing replacement XFS btrees. It is used by rebuild workflows, especially online repair, where a new btree must be built privately and then committed atomically by swapping the root into the live filesystem metadata.

The file deliberately separates staged construction from normal btree mutation. Regular btree operations are not supported on staging cursors; callers feed sorted records to the bulk loader and then commit the fake root through type-specific code.

## Staging cursor lifecycle

For AG-rooted btrees:
- `xfs_btree_stage_afakeroot` attaches a zeroed `struct xbtree_afakeroot` to a cursor, copies its current height, requires no transaction, and sets `XFS_BTREE_STAGING`.
- `xfs_btree_commit_afakeroot` clears the fake root pointer, restores the real AG buffer pointer and transaction, and clears staging mode. The caller must log the root change before this call.

For inode-rooted btrees:
- `xfs_btree_stage_ifakeroot` attaches a `struct xbtree_ifakeroot`, sets the cursor height, sets the staging fork size and fork selector, requires no transaction, and sets staging mode.
- `xfs_btree_commit_ifakeroot` clears the fake root pointer, restores the real fork selector and transaction, and clears staging mode. The caller must log the root change before committing.

The staging functions assert that the cursor type matches the fake root kind and that the cursor is not already staging.

## Bulk-load model

The bulk-load interface builds a whole btree from sorted records:
1. Caller initializes a fake root and staging cursor.
2. Caller fills an `xfs_btree_bload` descriptor.
3. `xfs_btree_bload_compute_geometry` computes height and block count.
4. Caller preallocates all blocks and exposes them through `claim_block`.
5. `xfs_btree_bload` formats all blocks bottom-up.
6. Caller commits the staged root to live metadata.

Preallocating every block is essential: bulk loading avoids mid-build ENOSPC failures and can lay out the new tree compactly.

## Buffer handling during loading

`xfs_btree_bload_drop_buf` queues a newly formatted btree buffer for delayed write, marks it up to date, releases it, and optionally flushes the ordered buffer list when `max_dirty` is reached. This throttles dirty buffers during large rebuilds.

`xfs_btree_bload_prep_block` allocates and initializes the next block at a given level:
- For inode-rooted root levels, it allocates an in-core root block using the caller's `iroot_size` callback and does not claim a disk block.
- For normal blocks, it calls the caller's `claim_block`, gets a buffer, links the previous block's right sibling to the new block, drops the previous buffer, initializes the new block header, sets its left sibling, and returns the new pointer/buffer/block.

Sibling links are therefore built incrementally left-to-right.

## Loading leaves and nodes

`xfs_btree_bload_leaf` fills a leaf block by repeatedly calling the caller's `get_records` callback. The callback receives the cursor, destination index, block pointer, number of wanted records, and private data. It returns the number loaded or a negative errno.

`xfs_btree_bload_node` fills an internal block with key/pointer entries. For each child pointer:
- It reads the child block.
- It copies the child pointer into the node.
- It derives the child low/high key summary with `xfs_btree_get_keys`.
- It copies the key into the node.
- It advances to the child's right sibling.

This builds parent levels from the leftmost block of the lower level upward.

## Geometry computation

`xfs_btree_bload_ensure_slack` normalizes caller slack values. Negative slack means approximately 75 percent fill, computed halfway between minrecs and maxrecs. Slack is capped so block occupancy cannot underflow below minimum records.

`xfs_btree_bload_max_npb` computes the maximum records or key/pointers to install in a block at a level. It respects inode-root maximum records for the root and subtracts leaf or node slack for regular blocks.

`xfs_btree_bload_desired_npb` clamps desired occupancy to at least minrecs for non-root levels and at least one entry for root levels.

`xfs_btree_bload_level_geometry` computes:
- Average items per block for a level.
- Number of blocks in the level.
- Number of leftmost blocks that receive one extra item to distribute uneven division.

It starts from desired occupancy, uses integer division so occupancy stays above the desired/minimum level, and increments block count if any block would exceed the absolute maximum.

`xfs_btree_bload_compute_geometry` uses these helpers from leaves upward. For inode-rooted btrees, it repeatedly recalculates geometry because the in-inode root has different capacity from regular blocks. It excludes the inode root from `nr_blocks` because it does not consume a separate filesystem block.

## Bulk-load execution

`xfs_btree_bload` performs the actual build:
- Initializes the buffer list, cursor height, dirty counter, and null child/current pointers.
- Computes leaf geometry and fills each leaf block with sorted records.
- Records the leftmost leaf pointer as the starting child pointer for the first node level.
- Flushes the final leaf buffer.
- For each internal level, computes geometry, creates node blocks, loads key/pointer pairs from the lower level, records the leftmost node pointer, and flushes the final block for that level.
- Updates the fake root with root pointer, height, and block count.
- Submits all delayed-write buffers and fails if the buffer list is unexpectedly non-empty afterward.
- Cancels any remaining delayed-write buffers and releases the active buffer on exit.

For inode-rooted btrees, the root pointer is expected to be null because the root is stored in the fake inode fork; the fake root records levels and block count excluding the in-core root. For AG-rooted btrees, the fake root stores the AG block root pointer, height, and total blocks.

## Important invariants

- Bulk loading requires `XFS_BTREE_STAGING`.
- Records supplied by `get_records` must already be sorted in btree order.
- All disk blocks must be preallocated and claimable before loading begins.
- Normal staged cursor mutation paths are intentionally blocked elsewhere in the btree core.
- Inode-rooted btree geometry must account for the special capacity of the in-inode root.
- The delayed-write list must be empty after final submission.
