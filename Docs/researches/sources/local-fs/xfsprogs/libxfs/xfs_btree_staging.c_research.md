# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.c

## Purpose

`xfs_btree_staging.c` implements fake-root staging cursors and the generic btree bulk loader. It is used to construct replacement XFS btrees privately, then commit the new root atomically into live metadata.

The file is byte-identical to the Linux-stable copy in this repository.

## Staging Cursor Model

A staging cursor has `XFS_BTREE_STAGING` set and points to a fake root instead of live AG or inode metadata. Regular btree queries and mutations are not supported for staging cursors; they are intended for bulk loading only.

Two fake-root families are supported:

- AG-rooted fake roots via `struct xbtree_afakeroot`.
- Inode-rooted fake roots via `struct xbtree_ifakeroot`.

## AG-Rooted Fake Roots

`xfs_btree_stage_afakeroot`:

- requires a non-inode btree cursor;
- requires no transaction;
- installs the fake root;
- copies fake-root height to the cursor;
- sets staging mode.

`xfs_btree_commit_afakeroot`:

- requires staging mode and no current transaction;
- clears the fake root;
- restores the real AG buffer and transaction;
- clears staging mode.

The caller must log the root change before commit.

## Inode-Rooted Fake Roots

`xfs_btree_stage_ifakeroot`:

- requires an inode-rooted cursor;
- requires no transaction;
- installs the fake inode fork root;
- copies fake-root height and fork size to the cursor;
- switches cursor fork selection to `XFS_STAGING_FORK`;
- sets staging mode.

`xfs_btree_commit_ifakeroot`:

- clears the fake inode root;
- restores the real fork selector and transaction;
- clears staging mode.

The caller must log the root change before commit.

## Bulk Loading Workflow

The bulk-loader comments describe the intended sequence:

1. Initialize a fake root.
2. Create a staging cursor.
3. Fill an `xfs_btree_bload` descriptor.
4. Call `xfs_btree_bload_compute_geometry`.
5. Preallocate every block reported in `nr_blocks`.
6. Call `xfs_btree_bload`.
7. Commit the staged root.
8. Clean up old btree blocks outside this generic code.

Bulk loading requires preallocated blocks to avoid ENOSPC failures midway through a rebuild and to improve locality.

## Dirty Buffer Handling

`xfs_btree_bload_drop_buf` marks newly formatted buffers uptodate, queues them for delayed write, releases the caller’s reference, and optionally flushes the delayed-write list after `max_dirty` buffers.

This prevents very large rebuilds from accumulating unbounded dirty buffers.

## Block Preparation

`xfs_btree_bload_prep_block` prepares the next block at a level.

For inode-rooted root levels:

- it allocates an incore fork-root buffer using the caller’s `iroot_size` callback;
- initializes the root block;
- returns no buffer pointer because the root lives in the inode fork;
- sets the block pointer to null.

For normal buffer-backed blocks:

- it claims a preallocated block via `claim_block`;
- obtains a buffer through generic btree helpers;
- updates the previous block’s right sibling pointer;
- drops the previous buffer to the delayed-write list;
- initializes the new block;
- sets its left sibling pointer;
- updates output pointers to the new block.

## Leaf Loading

`xfs_btree_bload_leaf` repeatedly calls the caller’s `get_records` callback until the requested number of records has been loaded into a leaf block.

The callback is responsible for returning records in btree sort order and usually does so by setting `cur->bc_rec` and using the concrete btree’s record initializer.

## Node Loading

`xfs_btree_bload_node` fills an internal node with key/pointer pairs:

- reads each child block;
- copies the child pointer into the node;
- derives child low/high keys with `xfs_btree_get_keys`;
- stores those keys in the parent;
- advances to the child’s right sibling;
- releases the child buffer.

This preserves both regular and overlapping-btree key summaries.

## Geometry Calculation

The loader computes tree geometry from record count, min/max records, and slack settings.

`xfs_btree_bload_ensure_slack` normalizes slack:

- negative slack means approximately 75 percent full;
- slack is capped so non-root blocks cannot fall below minimum occupancy.

`xfs_btree_bload_max_npb` computes the maximum entries to install at a level, respecting inode-root capacity for roots and subtracting leaf/node slack for ordinary blocks.

`xfs_btree_bload_desired_npb` enforces minimum occupancy for non-root blocks and at least one entry for roots.

`xfs_btree_bload_level_geometry` computes, for a level:

- average entries per block;
- number of blocks;
- number of blocks receiving one extra entry due to uneven division.

It spreads records/keyptrs as evenly as possible while never exceeding max records.

`xfs_btree_bload_compute_geometry` computes final height and block count from leaves upward. Inode-rooted btrees require repeated recalculation because inode fork-root capacity differs from ordinary block capacity. For inode-rooted btrees, the incore inode root is excluded from `nr_blocks`.

## Bulk Load Execution

`xfs_btree_bload` builds the staged btree bottom-up:

- loads all leaf blocks first;
- records the leftmost pointer for the next level;
- drops dirty buffers as it progresses;
- iteratively loads internal levels;
- tracks total block count;
- records the final root into the fake root;
- submits all delayed-write buffers;
- cancels remaining delayed writes and releases the current buffer on error.

For AG-rooted btrees it records root AG block, height, and block count in `afake`. For inode-rooted btrees it records height and block count in `ifake`.

## Dependencies

This file depends on:

- generic btree helpers from `xfs_btree.c`;
- staging structures from `xfs_btree_staging.h`;
- buffer delayed-write APIs;
- concrete btree callbacks supplied through `xfs_btree_bload`;
- tracepoints for staging and block loading.
