# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ondisk.h

This header provides compile-time assertions that XFS on-disk and UABI structures have expected sizes, offsets, and constant values.

Major responsibilities:
- Define assertion macros for structure size, member offset, constant value, and superblock field offsets.
- Implement `xfs_check_ondisk_structs`, called at init time to compile-check layout assumptions.
- Check file structures, space btrees, dir/attr structures, realtime structures, log structures, parent pointer ioctl structs, superblock fields, and selected ioctl UABI structures.

Important checked areas:
- Dinodes, dquots, bmbt records, symlink headers, timestamps.
- AGF/AGI/AGFL and btree block/key/record layouts.
- Attr and directory v2/v3 block/header layouts.
- Realtime superblock/buffer/root pointer structures.
- Log item formats from `xfs_log_format.h`.
- Physical log record headers.
- Parent pointer ioctl records.
- Superblock field offsets through `struct xfs_dsb` and `struct xfs_sb`.
- Bigtime and quota bigtime range conversions.
- Public ioctl struct sizes.

Purpose:
- Prevent compiler, architecture, or source changes from silently altering persistent disk format or userspace ABI.
- Preserve v4/v5 shared header offsets so older metadata fields remain findable at stable positions.

Risk notes:
- Some structures are intentionally omitted due to architecture-dependent padding.
- Any assertion change should be treated as disk-format or UABI review material.
- This file is a guardrail, not runtime validation; it catches layout drift at build time.
