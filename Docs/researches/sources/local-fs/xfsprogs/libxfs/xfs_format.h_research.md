# File Research: sources/local-fs/xfsprogs/libxfs/xfs_format.h

## Purpose
Defines the core XFS on-disk format shared by kernel-style libxfs code and userspace xfsprogs tooling. This is the authoritative layout contract for superblocks, AG headers, dinodes, quota records, symlink blocks, allocation/inode/rmap/refcount/bmap btree records, generic btree block headers, and ACL records.

## Main Contents
- Superblock format:
  - Defines historical superblock versions 1-5 and legacy `sb_versionnum` feature bits.
  - Defines v5 feature masks: compat, ro-compat, incompat, and log-incompat.
  - Supports modern flags including finobt, rmapbt, reflink, inobt block counts, sparse inodes, bigtime, large extent counts, exchange range, parent pointers, metadata directories, zoned realtime, and realtime LBA gaps.
  - Provides incore `struct xfs_sb` and ondisk `struct xfs_dsb`; changes here have repair-tool implications noted by comments.
- Address conversion macros:
  - Converts between fsblocks, AG numbers, AG blocks, disk addresses, bytes, and basic blocks.
  - Defines AG header block positions for superblock, AGF, AGI, and AGFL.
- AG metadata:
  - `struct xfs_agf` for free-space/rmap/refcount roots and counters.
  - `struct xfs_agi` for inode btree roots, free inode btree roots, inode counters, unlinked buckets, CRC/LSN, and inobt block counters.
  - `struct xfs_agfl` for AG freelist header.
- Realtime metadata:
  - Defines realtime bitmap/summary raw word storage, realtime group limits, realtime superblock `struct xfs_rtsb`, and realtime metadata btree root records.
- Time encoding:
  - Defines legacy timestamp bounds and bigtime timestamp conversion helpers.
  - Bigtime shifts XFS timestamp epoch to the legacy minimum timestamp range.
- Dinode format:
  - Defines `struct xfs_dinode`, fork access macros, inode flags, large extent count support, metadata inode constraints, device-number helpers, inode number bit slicing, and maximum inode numbers.
  - Data/attr fork sizes are derived from inode version, inode size, and `di_forkoff`.
- Quota format:
  - Defines dquot record types, bigtime quota expiry encoding, grace-period bounds, `struct xfs_disk_dquot`, and `struct xfs_dqblk`.
- Btree formats:
  - Allocation btree records and keys.
  - Inode allocation btree records, sparse inode holemask format, free masks, and inobt/finobt magic values.
  - Reverse mapping btree owners, records, key format, and offset flag packing.
  - Refcount btree records, CoW staging flag, and realtime refcount variants.
  - Bmap btree records, delayed allocation startblock encoding, max extent length, and generic short/long btree block headers.
- ACL/xattr format:
  - On-disk ACL structures and maximum entry calculations.
  - Well-known XFS ACL xattr names.

## Dependencies and Integration
- Consumed by most libxfs modules because it defines persistent metadata structures.
- Used directly by inode allocation code for `xfs_agi`, `xfs_inobt_rec`, inobt masks, inode number conversion, and btree magic values.
- Used by mount/feature logic through inline feature helpers such as `xfs_sb_is_v5`, `xfs_sb_has_*_feature`, and log-incompat helpers.
- Must remain synchronized with repair code and log-format code because layout changes affect recovery and xfs_repair validation.

## Invariants and Constraints
- Ondisk structures use explicit endian types; callers must convert via `cpu_to_be*` / `be*_to_cpu`.
- Superblock counter fields are intentionally contiguous for transaction delta application.
- AGI logging regions are split around the unlinked bucket array to avoid excessive log ranges.
- Metadata inode flags are deliberately restrictive to reduce userspace exposure risk.
- Inobt sparse records use a 16-bit holemask where nonzero bits mean physically missing inode subranges; free masks must be interpreted together with holemasks.
- Btree header sizes must be computed with macros, not `sizeof(struct xfs_btree_block)`.

## Notable Risks
- This file is ABI/persistent-format sensitive. Any field insertion, enum renumbering, or macro semantic change can break existing filesystems or userspace tooling.
- The macro `XFS_RMAP_IS_UNWRITTEN(len)` references `off` in its body; that depends on caller context or is a latent typo-style hazard.
- Feature-bit additions require coordinated updates in mkfs, mount validation, repair, scrub, geometry reporting, and compatibility checks.
