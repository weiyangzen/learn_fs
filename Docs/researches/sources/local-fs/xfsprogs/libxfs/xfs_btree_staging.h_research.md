# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_staging.h

## Purpose

`xfs_btree_staging.h` declares fake-root structures and the bulk-load API for constructing staged XFS btrees. It is the public interface implemented by `xfs_btree_staging.c`.

The file is byte-identical to the Linux-stable copy in this repository.

## AG Fake Root

`struct xbtree_afakeroot` stores:

- `af_root`: AG block number of the new btree root;
- `af_levels`: staged btree height;
- `af_blocks`: number of blocks used.

The header declares:

- `xfs_btree_stage_afakeroot`
- `xfs_btree_commit_afakeroot`

## Inode Fake Root

`struct xbtree_ifakeroot` stores:

- fake inode fork pointer;
- number of blocks used;
- staged btree height;
- bytes available in the inode fork.

The header declares:

- `xfs_btree_stage_ifakeroot`
- `xfs_btree_commit_ifakeroot`

## Bulk-Load Callback Types

The bulk loader is parameterized by three callbacks:

- `xfs_btree_bload_get_records_fn`: load sorted records into a leaf block.
- `xfs_btree_bload_claim_block_fn`: claim one preallocated block and return it as a generic btree pointer.
- `xfs_btree_bload_iroot_size_fn`: compute incore inode-root size for inode-rooted btrees.

## `struct xfs_btree_bload`

`struct xfs_btree_bload` carries both caller configuration and computed geometry:

- callbacks for records, block claiming, and inode-root sizing;
- planned record count;
- leaf and node slack;
- computed block count;
- computed btree height;
- dirty-buffer flush threshold;
- current dirty-buffer count.

Negative slack means the geometry code computes a default that leaves blocks roughly 75 percent full. Slack is not enforced on inode root blocks.

## Public API

The header declares:

- `xfs_btree_bload_compute_geometry`
- `xfs_btree_bload`

Callers must preallocate all blocks reported by geometry before invoking the actual bulk load.
