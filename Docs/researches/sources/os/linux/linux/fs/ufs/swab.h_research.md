# File Research: sources/os/linux/linux/fs/ufs/swab.h

## Purpose
Provides filesystem-endian conversion helpers for UFS on-disk 16-, 32-, and 64-bit fields.

## Main Contents
- Defines `BYTESEX_LE` and `BYTESEX_BE`.
- Conversion helpers:
  - `fs64_to_cpu()`, `cpu_to_fs64()`
  - `fs32_to_cpu()`, `cpu_to_fs32()`
  - `fs16_to_cpu()`, `cpu_to_fs16()`
- In-place arithmetic helpers:
  - `fs32_add()`, `fs32_sub()`
  - `fs16_add()`, `fs16_sub()`

## Important Design Points
- All conversions are controlled by `UFS_SB(sbp)->s_bytesex`, which is set during superblock magic probing.
- The file assumes UFS instances are either little-endian or big-endian; exotic mixed-endian formats are explicitly outside its design.
- Uses Linux endian helpers with `__force` casts for bitwise on-disk typedefs.

## Cross-File Relationships
- Included by `super.c`, `util.c`, and `util.h`.
- Requires `UFS_SB()` from `ufs.h`.
- Applies to on-disk typedefs declared in `ufs_fs.h`: `__fs16`, `__fs32`, and `__fs64`.

## Risks / Review Notes
- Any missed conversion at a caller can corrupt metadata on opposite-endian UFS images.
- In-place add/sub helpers cast typed pointers to endian-specific pointer types; callers must pass actual on-disk fields, not CPU-native temporary storage.
