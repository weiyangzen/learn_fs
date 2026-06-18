# File Research: sources/local-fs/e2fsprogs/misc/filefrag.c

## Purpose
Implements `filefrag`, reporting extent count and optional detailed extent layout for files.

## Key Elements
Provides a non-Linux stub that exits unsupported. On Linux, parses `-Bb::eEkPsvVxX`, opens each file, determines filesystem block size via `FIGETBSZ`/`fstatfs`, and calculates logical/physical display widths.

Primary path uses `FS_IOC_FIEMAP` or ext4 `EXT4_IOC_GET_ES_CACHE`, printing known FIEMAP flags and counting discontinuities as extents. Fallback path uses `FIBMAP`, with extra accounting for ext2/ext3 indirect blocks and optional forced extent-style output. Supports sync-before-map, xattr map requests, extent cache preload/query, 1K or custom output block size, and hex output.

## Dependencies
Uses Linux ioctls `FS_IOC_FIEMAP`, `FIBMAP`, `FIGETBSZ`, ext4 flags/ioctls from e2fsprogs headers, `statfs`, `fstat`, `open64`/`fstat64` where available, and e2fsprogs helpers such as `ext2fs_log10_u64`.

## Behavior/Risks
FIBMAP may require root and may be unsupported; FIEMAP can reject incompatible flags. Ext4 extent status cache options are explicitly ext4/kernel dependent. The program returns the negated first negative errno encountered across files.
