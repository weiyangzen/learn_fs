# File Research: sources/os/linux/linux/fs/f2fs/Kconfig

## Purpose
Defines F2FS kernel configuration options and dependency wiring.

## Key Options
- `F2FS_FS`: main filesystem support, depends on `BLOCK`, selects buffer heads, NLS, CRC32, iomap, and encryption/xattr helpers when needed.
- `F2FS_STAT_FS`: debugfs status reporting.
- `F2FS_FS_XATTR`: extended attributes, default enabled.
- `F2FS_FS_POSIX_ACL`: POSIX ACLs, depends on xattrs and selects `FS_POSIX_ACL`.
- `F2FS_FS_SECURITY`: security labels through xattrs.
- `F2FS_CHECK_FS`: runtime consistency checking.
- `F2FS_FAULT_INJECTION`: test fault injection.
- `F2FS_FS_COMPRESSION`: filesystem-level compression.
- Compression backends: LZO, LZO-RLE, LZ4, LZ4HC, ZSTD.
- `F2FS_IOSTAT`: sysfs and tracepoint IO statistics.
- `F2FS_UNFAIR_RWSEM`: unfair rwsem behavior for block-cgroup priority systems.

## Build Impact
This file controls which optional objects in the F2FS Makefile are compiled, especially `xattr.o`, `acl.o`, `compress.o`, `debug.o`, and `iostat.o`.
