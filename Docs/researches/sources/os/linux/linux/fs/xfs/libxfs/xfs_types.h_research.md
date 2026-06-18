# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.h

## Purpose

`xfs_types.h` defines fundamental XFS scalar types, null sentinels, size limits, fork identifiers, record structures, reservation enums, group/free-counter enums, and type verifier declarations.

## Main Content

- Defines scalar types for:
  - AG/RT group block numbers.
  - AG/RT group numbers.
  - extent lengths and counts.
  - file sizes and offsets.
  - realtime bitmap words/summary offsets.
  - log sequence numbers.
  - filesystem and realtime block addresses.
- Defines `xfs_failaddr_t` for verifier failure sites.
- Defines null sentinel constants for blocks, AGs, RT groups, file offsets, inodes, and LSNs.
- Defines minimum/maximum filesystem block and sector sizes.
- Defines inode fork identifiers, including staging, data, attr, and CoW forks.
- Defines lookup modes and trace string mappings.
- Defines name structure and dquot id type.
- Defines realtime bitmap bit-manipulation constants.
- Defines extent cursor, bmap extent record, extent state, refcount domain, refcount record, and rmap record.
- Defines rmap flags and key/record flag masks.
- Defines AG reservation types.
- Defines btree record packing scan results.
- Defines generic group types: AG and realtime group.
- Defines free counter types:
  - data blocks.
  - realtime extents.
  - zoned realtime available extents.
- Declares type verifier functions.

## Key Interfaces and Invariants

- `xfs_rfsblock_t` represents raw filesystem block numbers distinct from encoded filesystem block numbers.
- `xfs_rtblock_t` is a block address in realtime space, not necessarily a realtime extent number.
- `XFS_STAGING_FORK` is a fake fork id used for staging btrees.
- Rmap key flags exclude unwritten state; unwritten is a record flag.
- `XC_FREE_RTAVAILABLE` is meaningful for zoned realtime devices and differs from total free realtime extents.

## Dependencies

This foundational header is consumed broadly by libxfs and kernel XFS code; verifier declarations depend only on a forward-declared `struct xfs_mount`.
