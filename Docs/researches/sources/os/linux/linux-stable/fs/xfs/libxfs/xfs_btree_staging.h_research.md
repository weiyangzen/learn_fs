# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_staging.h

## Role in the repository

`xfs_btree_staging.h` declares the fake-root structures and bulk-load API used to build replacement XFS btrees outside the live metadata root. It is the public header for staging cursors implemented in `xfs_btree_staging.c`.

## Fake roots

`struct xbtree_afakeroot` represents an AG-rooted btree under construction:
- `af_root`: AG block number of the new root.
- `af_levels`: height of the staged tree.
- `af_blocks`: number of blocks used by the staged tree.

`struct xbtree_ifakeroot` represents an inode-rooted btree under construction:
- `if_fork`: fake inode fork that owns the staged in-core root.
- `if_blocks`: number of disk blocks used by the staged btree.
- `if_levels`: height of the staged tree.
- `if_fork_size`: bytes available for the fork in the inode.

The header declares stage and commit functions for both fake root types.

## Bulk-load callback types

The header defines three callbacks:
- `xfs_btree_bload_get_records_fn`: load sorted records into a leaf block by setting cursor state and using the concrete btree record initializer.
- `xfs_btree_bload_claim_block_fn`: claim a preallocated block and return it as a generic btree pointer.
- `xfs_btree_bload_iroot_size_fn`: compute the byte size needed for an inode-rooted in-core root block.

These callbacks keep the generic loader independent from concrete record formats and allocation strategies.

## `struct xfs_btree_bload`

`struct xfs_btree_bload` carries all state for geometry and execution:
- Required callbacks: `get_records`, `claim_block`, and optional inode-root `iroot_size`.
- Input count: `nr_records`.
- Slack controls: `leaf_slack` and `node_slack`; negative values request automatic approximately 75 percent fill.
- Computed geometry: `nr_blocks` and `btree_height`.
- Dirty-buffer throttling: `max_dirty` and `nr_dirty`.

The public functions are:
- `xfs_btree_bload_compute_geometry`, which computes height and blocks for a planned record count.
- `xfs_btree_bload`, which formats and writes the staged tree.

## Important invariants

- Callers must use a staging cursor.
- Callers must preallocate every block reported by geometry before calling `xfs_btree_bload`.
- Inode-rooted callers must provide root sizing when the root can live in an inode fork.
- Slack controls affect regular btree blocks but are not enforced on inode root blocks.
