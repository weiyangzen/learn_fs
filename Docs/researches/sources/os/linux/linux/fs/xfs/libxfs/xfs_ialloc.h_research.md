# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.h

## Purpose

`xfs_ialloc.h` is the public libxfs header for inode allocation. It declares allocator/freeing/mapping entry points, AGI helpers, inobt helpers, inode chunk initialization, geometry setup, and shrink checks.

## Main Content

- Defines `XFS_INODE_BIG_CLUSTER_SIZE` as the large inode cluster target size.
- Defines `struct xfs_icluster`:
  - Indicates whether a chunk was deleted.
  - Carries first inode number.
  - Carries physical allocation bitmap for sparse chunks.
- Defines `xfs_make_iptr`, converting a buffer and inode offset into an on-disk dinode pointer.
- Declares top-level inode allocation/freeing:
  - `xfs_dialloc`.
  - `xfs_difree`.
- Declares inode mapping:
  - `xfs_imap`.
- Declares AGI logging and reading:
  - `xfs_ialloc_log_agi`.
  - `xfs_read_agi`.
  - `xfs_ialloc_read_agi`.
  - `XFS_IALLOC_FLAG_TRYLOCK`.
- Declares inobt operations:
  - `xfs_inobt_lookup`.
  - `xfs_inobt_get_rec`.
  - `xfs_inobt_rec_freecount`.
  - `xfs_inobt_btrec_to_irec`.
  - `xfs_inobt_check_irec`.
  - `xfs_inobt_insert_rec`.
- Declares inode chunk initialization:
  - `xfs_ialloc_inode_init`.
- Declares analysis/counting helpers:
  - `xfs_ialloc_has_inodes_at_extent`.
  - `xfs_ialloc_count_inodes`.
- Declares geometry and mkfs-layout helpers:
  - `xfs_ialloc_cluster_alignment`.
  - `xfs_ialloc_setup_geometry`.
  - `xfs_ialloc_calc_rootino`.
  - `xfs_ialloc_check_shrink`.

## Key Interfaces and Invariants

- `xfs_dialloc` returns an on-disk inode number and can roll the transaction pointer.
- `xfs_difree` takes a per-AG object matching the inode’s AG and reports whether an inode cluster was deleted.
- `xfs_imap` supports trusted fast paths and untrusted btree-backed validation.
- Inode records are always exposed through `xfs_inobt_rec_incore_t`, hiding sparse/non-sparse on-disk format differences.

## Dependencies

Forward declares core XFS allocation, transaction, mount, inode buffer, btree, and per-AG structures. Implemented primarily by `xfs_ialloc.c`.
