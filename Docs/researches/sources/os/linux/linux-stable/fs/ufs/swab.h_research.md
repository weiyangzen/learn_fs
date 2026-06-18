# File Research: sources/os/linux/linux-stable/fs/ufs/swab.h

## Summary
Defines filesystem-endian conversion helpers for UFS media that may be little-endian or big-endian.

## Main Contents
- Byte-order selector enum: `BYTESEX_LE`, `BYTESEX_BE`.
- Conversion helpers: `fs64_to_cpu()`, `cpu_to_fs64()`, `fs32_to_cpu()`, `cpu_to_fs32()`, `fs16_to_cpu()`, `cpu_to_fs16()`.
- In-place arithmetic helpers: `fs32_add()`, `fs32_sub()`, `fs16_add()`, `fs16_sub()`.

## Important Behavior
All helpers branch on `UFS_SB(sb)->s_bytesex`, which is set during superblock probing. The file assumes UFS media are either little-endian or big-endian, not mixed or unusual byte orders.

## Dependencies
Requires `UFS_SB()` from UFS in-core state and Linux endian conversion primitives.

## Risks
Every on-disk numeric access depends on `s_bytesex` being detected before use. Incorrect byte sex causes geometry, counters, inode fields, and bitmaps to be interpreted incorrectly.
