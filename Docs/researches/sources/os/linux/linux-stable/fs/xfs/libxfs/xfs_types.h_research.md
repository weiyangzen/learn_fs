# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.h

## Purpose

Defines core XFS scalar types, null sentinels, block/sector limits, fork identifiers, common metadata records, group types, free counter identifiers, and type-verifier function declarations.

## Main Type Definitions

- Allocation group and realtime group block types:
  - `xfs_agblock_t`
  - `xfs_rgblock_t`
  - `xfs_agino_t`
  - `xfs_agnumber_t`
  - `xfs_rgnumber_t`
- Filesystem and realtime block types:
  - `xfs_fsblock_t`
  - `xfs_rfsblock_t`
  - `xfs_rtblock_t`
  - `xfs_rtxnum_t`
  - `xfs_rtbxlen_t`
- File offset and extent types:
  - `xfs_fileoff_t`
  - `xfs_filblks_t`
  - `xfs_extnum_t`
  - `xfs_extlen_t`
- Log sequence types:
  - `xfs_lsn_t`
  - `xfs_csn_t`

## Main Structures and Enums

- `struct xfs_name`
- `struct xfs_iext_cursor`
- `struct xfs_bmbt_irec`
- `enum xfs_refc_domain`
- `struct xfs_refcount_irec`
- `struct xfs_rmap_irec`
- `enum xfs_ag_resv_type`
- `enum xbtree_recpacking`
- `enum xfs_group_type`
- `enum xfs_free_counter`

## Important Constants

- Null sentinels:
  - `NULLFSBLOCK`
  - `NULLRTBLOCK`
  - `NULLAGBLOCK`
  - `NULLRGNUMBER`
  - `NULLFSINO`
- Block and sector limits:
  - `XFS_MIN_BLOCKSIZE`
  - `XFS_MAX_BLOCKSIZE`
  - `XFS_MIN_CRC_BLOCKSIZE`
  - `XFS_MIN_SECTORSIZE`
  - `XFS_MAX_SECTORSIZE`
- Fork identifiers:
  - `XFS_DATA_FORK`
  - `XFS_ATTR_FORK`
  - `XFS_COW_FORK`
  - `XFS_STAGING_FORK`

## Rtgroup and Zoned Additions

- `XG_TYPE_RTG` identifies realtime groups alongside allocation groups.
- `XC_FREE_RTEXTENTS` tracks free realtime extents.
- `XC_FREE_RTAVAILABLE` tracks immediately usable realtime extents for zoned realtime filesystems.

## Research Notes

This header is foundational. The realtime group and zoned free-counter additions make generic group and free-space code capable of handling both data-device AGs and realtime groups.
