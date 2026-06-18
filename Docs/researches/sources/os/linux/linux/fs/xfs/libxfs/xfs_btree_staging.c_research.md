# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.c

## Purpose

`xfs_btree_staging.c` implements staged btree rebuild support and the generic bulk loader for newly built btrees. It lets online repair and rebuild code construct a replacement btree behind a fake root, fill it from sorted records, and later atomically commit the new root into AG or inode metadata.

Staging cursors are intentionally restricted: regular btree modification operations are not supported. The bulk loader is the intended construction path.

## Fake Root Model

The file supports two fake root types:

- AG-rooted fake roots through `struct xbtree_afakeroot`.
- Inode-rooted fake roots through `struct xbtree_ifakeroot`.

A staging cursor points at these fake roots instead of live filesystem metadata. After bulk loading, the caller logs the real metadata root change and commits the fake root back into a normal cursor.

## AG-Rooted Staging

`xfs_btree_stage_afakeroot`:

- Requires a non-staging, non-inode, transactionless cursor.
- Stores `afake` in the cursor.
- Sets cursor height from `afake->af_levels`.
- Marks the cursor with `XFS_BTREE_STAGING`.

`xfs_btree_commit_afakeroot`:

- Requires a staging, transactionless cursor.
- Clears the fake root pointer.
- Restores the real AG buffer.
- Clears the staging flag.
- Attaches the transaction.

The caller must log the concrete AG root field before committing the staged cursor.

## Inode-Rooted Staging

`xfs_btree_stage_ifakeroot`:

- Requires an inode-rooted, non-staging, transactionless cursor.
- Stores the fake root.
- Sets cursor height from `ifake->if_levels`.
- Sets the cursor fork size and `XFS_STAGING_FORK`.
- Marks the cursor as staging.

`xfs_btree_commit_ifakeroot` clears fake-root state, restores the real fork selector, clears staging, and attaches the transaction.

The fake inode root owns a temporary `struct xfs_ifork`, block count, height, and available fork size.

## Bulk Load Workflow

The staged bulk-load sequence is:

1. Caller initializes a fake root and staging cursor.
2. Caller fills `struct xfs_btree_bload`.
3. Caller invokes `xfs_btree_bload_compute_geometry`.
4. Caller preallocates all blocks required by `bbl->nr_blocks`.
5. `xfs_btree_bload` formats blocks and loads sorted records.
6. Caller commits the staged root and later cleans up old btree blocks.

Preallocating all blocks avoids ENOSPC halfway through a rebuild and allows block placement policy to remain outside the loader.

## Buffer Handling

`xfs_btree_bload_drop_buf` marks a formatted buffer uptodate, queues it on an ordered delayed-write list, releases it, increments the dirty count, and submits the list when `max_dirty` is reached. The final loader submits all remaining buffers and cancels any list on error.

This bounds dirty buffer accumulation during large rebuilds.

## Block Preparation

`xfs_btree_bload_prep_block` creates one block at a given level:

- If the level is an inode root, it allocates `if_broot` memory through the caller’s `iroot_size` callback and initializes an inline root block.
- Otherwise it claims a preallocated block via `bbl->claim_block`.
- It gets the buffer for that block.
- It connects the previous block’s right sibling to the new block.
- It drops the previous buffer if needed.
- It initializes the new block header and left sibling.
- It returns the new pointer, buffer, and block.

This function is responsible for sibling linkage during level construction.

## Leaf Loading

`xfs_btree_bload_leaf` repeatedly calls `bbl->get_records` until the requested number of records has been written into the leaf block. The callback must return records in sorted order by setting cursor state and using concrete btree record initialization behavior.

A negative callback result aborts the load.

## Node Loading

`xfs_btree_bload_node` fills an internal block from lower-level child blocks:

- It reads the child block named by `child_ptr`.
- It copies `child_ptr` into the parent pointer slot.
- It derives the child low/high key summary through `xfs_btree_get_keys`.
- It copies the key into the parent.
- It advances `child_ptr` to the child’s right sibling.

This builds parent levels left-to-right from already formatted child levels.

## Geometry Calculation

`xfs_btree_bload_compute_geometry` determines final height and block count. It first normalizes slack:

- Negative slack means fill roughly halfway between min and max occupancy, generally about 75 percent full.
- Slack is capped so records per block never drops below minrecs for normal blocks.

For each level, `xfs_btree_bload_level_geometry` computes:

- Desired records/keyptrs per block.
- Number of blocks at this level.
- Average records per block.
- Count of leftmost blocks that receive one extra item.

Inode-rooted btrees are special because root geometry differs from regular blocks. The function recalculates level geometry when deciding whether contents fit in the inode root.

The final output fields are `bbl->nr_records`, `bbl->nr_blocks`, and `bbl->btree_height`. For inode-rooted btrees, the inline root is not counted in `nr_blocks`.

## Bulk Load Execution

`xfs_btree_bload`:

- Sets cursor height to the computed btree height.
- Loads leaf blocks first, distributing records evenly and remembering the leftmost leaf pointer.
- Drops/submits dirty buffers as configured.
- Builds each internal level from the child level’s sibling chain.
- Updates the fake root with root pointer, height, and block count.
- Submits all formatted buffers.
- Cancels outstanding delayed-write buffers and releases the current buffer on error.

For inode-rooted btrees, the top level can be an inline root and the fake root records `if_levels` and `if_blocks`. For AG-rooted btrees, the fake root records `af_root`, `af_levels`, and `af_blocks`.

## Integration Points

This file depends on generic btree layout/access helpers from `xfs_btree.c`, concrete btree callbacks supplied in `xfs_btree_ops`, caller-provided reservation/record callbacks from `xfs_btree_bload`, transactionless staging cursors, and delayed-write buffer submission.

It is primarily used by online repair and rebuild paths that need to construct replacement metadata off to the side.

## Important Invariants

- Staging cursors must be transactionless until committed.
- Bulk records must be supplied in sort order.
- All disk blocks must be preallocated and claimed through the loader callback.
- Regular btree modification paths must not be used on staging cursors.
- Inode-root bulk loading requires an `iroot_size` callback.
- The fake root is the only root visible until the caller commits it.
