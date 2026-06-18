# File Research: sources/local-fs/jfsutils/libfs/devices.c

Device validation, size discovery, raw block I/O, and flushing helpers.

Key contents:
- Forces `_LARGEFILE_SOURCE` before `config.h` to avoid an autoconf/glibc `fseeko` issue.
- Includes platform headers for Linux/BSD/DragonFly disk size handling.
- Defines fallback Linux `BLKGETSIZE64` and `BLKGETSIZE` ioctl constants when needed.
- `ujfs_device_is_valid()` accepts block devices or regular files on Linux-like systems, character devices or regular files on DragonFly.
- `ujfs_get_dev_size()`:
  - For regular files, uses file size rounded down to 1024-byte multiple.
  - Uses `BLKGETSIZE64` or `BLKGETSIZE` on Linux when available.
  - Uses DragonFly slices/disklabel or BSD disklabel paths when available.
  - Falls back to exponential seek/read then binary search to find the last readable byte, restoring original file position.
- `ujfs_rw_diskblocks()` seeks to byte offset and reads/writes exact byte counts using `fread`/`fwrite`, returning Windows-like error codes from `devices.h`.
- `ujfs_flush_dev()` calls `fsync()` and optionally `BLKFLSBUF` except for ramdisks.

Interactions:
- Used by fscklog extraction, superblock helpers, mkfs, fsck, and log utilities for raw disk access.
- Error constants and operation modes come from `devices.h`.

Research notes:
- In `ujfs_get_dev_size()`, the exponential loop condition compares `Read_Result == 1`, but `fgetc()` returns a byte value or EOF; only byte value 1 continues, which appears suspect. The fallback may under-detect sizes depending on data byte read.
- `ujfs_rw_diskblocks()` checks `Bytes_Transferred == -1`, but `size_t` cannot equal `-1` in the intended way.
