# File Research: sources/os/linux/linux-stable/fs/befs/endian.h

This header provides BeFS endian conversion helpers for scalar and composite on-disk types.

Scalar helpers:
- `fs64_to_cpu()` / `cpu_to_fs64()`
- `fs32_to_cpu()` / `cpu_to_fs32()`
- `fs16_to_cpu()` / `cpu_to_fs16()`

Composite helpers:
- `fsrun_to_cpu()` converts `befs_disk_block_run` to `befs_block_run`.
- `cpu_to_fsrun()` converts a host block run to disk endian format.
- `fsds_to_cpu()` converts a full on-disk datastream, including all direct runs and range limits.

Integration:
- Included at the end of `befs.h` because conversion depends on `BEFS_SB(sb)->byte_order`.
- Used throughout BeFS superblock, inode, datastream, btree, and debug code.

Risk notes:
- `BEFS_SB(sb)->byte_order` must be initialized before these helpers are used. `befs_load_sb()` sets it based on `fs_byte_order`.
- No fallback branch handles an invalid byte-order marker; callers rely on superblock validation and magic checks to reject unusable state.
