# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ondisk.h

## Role

This header provides compile-time assertions for XFS on-disk and UAPI structure sizes, field offsets, and constant values. It is a guard against accidental ABI or disk-format layout drift.

## Main Mechanism

Macros wrap `static_assert` for:

- structure size checks
- member offset checks
- constant value checks
- paired superblock disk/incore offset checks

`xfs_check_ondisk_structs` runs these assertions at compile time.

## Checked Areas

The checks cover:

- file structures such as ACLs, bmap records, dinodes, dquots, symlink headers, and timestamps
- allocation, inode, rmap, and refcount btree structures
- dir and attr v4/v5 structures
- realtime superblock, bitmap/summary words, rt buffer headers, and realtime btree roots
- parent pointer records
- log structures including inode, buffer, extent intent, attr intent, bmap/rmap/refcount intent, mapping exchange, and log record headers
- v5 structures retaining v4 magic/header offsets
- bigtime and quota bigtime converted range constants
- superblock disk/incore size and all major field offsets
- ioctl UAPI structures such as bulkstat, inumbers, bmap, attrlist, geometry, scrub, and fs counts

## Compatibility Notes

Some checks are intentionally omitted or commented where architecture-specific padding or legacy definitions make size checks unreliable, such as old attr remote-name details and some ioctl structures.

## Dependencies

This header depends on nearly all core on-disk format structure definitions, log format definitions, ioctl UAPI structs, and compile-time assertion support.

## Research Notes

This file is a high-signal compatibility tripwire. When modifying any on-disk, log, or ioctl structure, this file must be updated deliberately and in sync with recovery, mkfs, repair, and kernel/userspace ABI expectations.
