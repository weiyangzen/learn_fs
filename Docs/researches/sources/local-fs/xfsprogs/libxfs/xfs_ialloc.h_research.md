# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.h

## Purpose
Declares the inode allocation public interface for libxfs: inode allocation/freeing, inode number mapping, AGI reads/logging, inobt operations, inode chunk initialization, inobt record validation/counting, geometry setup, root inode calculation, and shrink checks.

## Main Contents
- Constants and helper types:
  - `XFS_INODE_BIG_CLUSTER_SIZE` defines the target inode cluster movement size.
  - `struct xfs_icluster` reports whether a freed inode caused chunk deletion, the first inode, and physical allocation bitmap for sparse chunks.
- Helper:
  - `xfs_make_iptr` maps a buffer plus inode index to an ondisk dinode pointer.
- Allocation/free APIs:
  - `xfs_dialloc` allocates an ondisk inode.
  - `xfs_difree` frees an ondisk inode and reports chunk-level deletion state.
- Mapping/read APIs:
  - `xfs_imap` converts inode number to buffer mapping information.
  - `xfs_read_agi` and `xfs_ialloc_read_agi` read AGI buffers; `XFS_IALLOC_FLAG_TRYLOCK` controls trylock behavior.
- Btree record APIs:
  - `xfs_inobt_lookup`, `xfs_inobt_get_rec`, `xfs_inobt_rec_freecount`, `xfs_inobt_insert_rec`.
  - `xfs_inobt_btrec_to_irec` and `xfs_inobt_check_irec`.
- Higher-level helpers:
  - `xfs_ialloc_inode_init`.
  - `xfs_ialloc_has_inodes_at_extent`.
  - `xfs_ialloc_count_inodes`.
  - `xfs_ialloc_cluster_alignment`, `xfs_ialloc_setup_geometry`, `xfs_ialloc_calc_rootino`.
  - `xfs_ialloc_check_shrink`.

## Dependencies and Integration
- Implemented mainly by `xfs_ialloc.c`; cursor creation and masks come from `xfs_ialloc_btree.c/h`.
- Exposes functions used by inode creation/removal, scrub/repair, mkfs/recovery-style initialization, grow/shrink code, and inode lookup code.

## Invariants
- Callers freeing an inode must pass a perag matching the inode AG.
- `xfs_imap` accepts flags affecting trust and lookup behavior.
- Inobt record helpers return normalized incore records regardless of sparse inode feature encoding.
- `struct xfs_icluster.alloc` describes physical inode allocation, not logical free/allocated inode state.

## Notable Risks
- This header is a narrow public boundary for inode allocation internals; signature changes ripple across inode, scrub, repair, and mkfs code.
- The declaration `xfs_ialloc_cluster_alignment` is present here but not defined in the read file, so implementation is elsewhere in the source tree.
