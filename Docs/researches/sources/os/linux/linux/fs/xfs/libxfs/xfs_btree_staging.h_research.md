# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_staging.h

## Purpose

`xfs_btree_staging.h` declares fake-root state and bulk-loading interfaces for staged XFS btree construction.

## Fake Root Types

`struct xbtree_afakeroot` tracks a staged AG-rooted btree:

- New root AG block.
- New height.
- Number of blocks used.

`struct xbtree_ifakeroot` tracks a staged inode-rooted btree:

- Temporary inode fork.
- Block count.
- Height.
- Available fork size.

These are stored in staging cursors while a replacement btree is being built.

## Stage and Commit APIs

The header declares:

- `xfs_btree_stage_afakeroot`
- `xfs_btree_commit_afakeroot`
- `xfs_btree_stage_ifakeroot`
- `xfs_btree_commit_ifakeroot`

Stage functions redirect a cursor to fake root state. Commit functions transform the cursor back to normal metadata-rooted operation after the caller logs the real root update.

## Bulk-Load Callbacks

The bulk loader is parameterized by:

- `xfs_btree_bload_get_records_fn`: supplies sorted records for leaf blocks.
- `xfs_btree_bload_claim_block_fn`: claims one preallocated block for formatting.
- `xfs_btree_bload_iroot_size_fn`: computes inline inode-root buffer size.

The loader does not allocate arbitrary filesystem space itself; callers must reserve and claim blocks.

## `struct xfs_btree_bload`

This structure contains loader callbacks, input record count, slack targets, computed block count and height, dirty-buffer flush thresholds, and dirty-buffer accounting.

Important fields:

- `nr_records`: caller input and geometry basis.
- `leaf_slack` / `node_slack`: free slots to leave in blocks, or negative for default 75 percent style loading.
- `nr_blocks`: computed number of external btree blocks.
- `btree_height`: computed tree height.
- `max_dirty`: delayed-write flush threshold.
- `nr_dirty`: runtime dirty buffer count.

## Exported Functions

- `xfs_btree_bload_compute_geometry`: prepares block count and height before allocation.
- `xfs_btree_bload`: formats and fills the staged btree.

## Integration Points

Concrete rebuild code includes this header to stage cursors and bulk-load replacement btrees. It must supply record iteration, block reservation/claiming, and inline-root sizing behavior suitable for the concrete btree type.

## Important Invariants

- Callers must compute geometry before loading.
- Callers must allocate all required blocks before `xfs_btree_bload`.
- Record callbacks must return records in sorted order.
- Slack values are advisory but bounded by btree min/max occupancy rules.
