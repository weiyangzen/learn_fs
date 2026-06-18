# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ondisk.h

## Role
`xfs_ondisk.h` performs compile-time assertions for XFS on-disk and UAPI structure sizes, member offsets, and constant values. It protects persistent metadata, journal formats, ioctl ABI, and compatibility layout assumptions from accidental C structure drift.

## Main Responsibilities
- Define assertion helpers for structure size, member offset, constant value, and matching superblock offsets in disk and in-core superblock structures.
- Check file metadata structures such as dinodes, bmbt records, dquots, symlink headers, and timestamps.
- Check AG and btree structures for allocation, inode, refcount, rmap, and realtime btrees.
- Check directory and attribute v2/v3 layout structures and shared prefix offsets.
- Check log item structures and physical log record headers.
- Check parent pointer ioctl and general XFS ioctl UABI structures.
- Check superblock field offsets, including newer metadir and realtime group fields.
- Check bigtime and quota bigtime conversion boundary constants.

## Data and Invariants
- v5 structures must preserve v4-compatible magic/header offsets at the start of metadata blocks.
- Some historically architecture-sensitive structures are checked through explicit 32-bit and 64-bit variants.
- Some structures are intentionally omitted where architecture-dependent padding or legacy layout makes exact checks unsuitable.
- Parent pointer record size is fixed at 12 bytes.
- Log structures such as inode log format, attr intent, exchange mapping intent, and physical record headers have fixed sizes.

## Dependencies
This header depends on all relevant XFS on-disk format headers being included before `xfs_check_ondisk_structs` is compiled. It is normally used during initialization/build validation.

## Research Notes
This file is a layout tripwire. It contains no operational filesystem logic, but it is essential for preventing silent ABI or disk-format breakage from structure edits.
