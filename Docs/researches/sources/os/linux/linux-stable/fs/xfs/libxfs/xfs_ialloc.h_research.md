# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.h

## Role in the repository

`xfs_ialloc.h` declares the public libxfs interface for inode allocation, inode freeing, inode mapping, AGI reading/logging, INOBT record lookup/access, inode chunk initialization, inode count queries, inode geometry setup, and shrink checks.

## Main definitions

`XFS_INODE_BIG_CLUSTER_SIZE` sets the preferred large inode cluster size to 8192 bytes.

`struct xfs_icluster` reports inode chunk deletion state to callers of `xfs_difree`. It records whether a chunk was deleted, the first inode number, and the physical allocation bitmap for sparse chunks.

`xfs_make_iptr` computes an on-disk dinode pointer within an inode buffer from a buffer pointer and inode index.

## Allocation and freeing API

`xfs_dialloc` allocates one on-disk inode and may roll the caller’s transaction. `xfs_difree` frees one on-disk inode and reports whether its containing inode chunk was removed.

`xfs_ialloc_inode_init` initializes newly allocated inode buffers for a chunk or sparse chunk.

## Mapping and AGI API

`xfs_imap` maps an inode to an `xfs_imap` location suitable for reading the inode buffer.

`xfs_ialloc_log_agi`, `xfs_read_agi`, and `xfs_ialloc_read_agi` expose AGI logging and verified AGI reads. `XFS_IALLOC_FLAG_TRYLOCK` requests trylock behavior for AGI buffer locking.

## INOBT helpers

The header declares:
- `xfs_inobt_lookup`
- `xfs_inobt_get_rec`
- `xfs_inobt_rec_freecount`
- `xfs_inobt_btrec_to_irec`
- `xfs_inobt_check_irec`
- `xfs_inobt_insert_rec`

It also exposes extent packing classification, inode counting, inode allocation geometry setup, root inode calculation, and shrink validation helpers.

## Important invariants

- Callers of `xfs_dialloc` must pass a transaction pointer by address because allocation can roll the transaction.
- `xfs_difree` requires the caller to supply the correct per-AG for the inode.
- `xfs_icluster.alloc` is a physical allocation bitmap for sparse chunks, not the logical free-inode mask.
- AGI reads use verifier-backed buffers and update per-AG cached state on first initialization.
