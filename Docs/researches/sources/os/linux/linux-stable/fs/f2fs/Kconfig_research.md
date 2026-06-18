# File Research: sources/os/linux/linux-stable/fs/f2fs/Kconfig

## Purpose
Defines kernel configuration options for F2FS filesystem support and optional features.

## Main Components
- `F2FS_FS` is a tristate depending on `BLOCK`; it selects buffer heads, NLS, CRC32, iomap, and crypto/compression helpers as needed.
- `F2FS_STAT_FS` enables debugfs status reporting.
- `F2FS_FS_XATTR`, `F2FS_FS_POSIX_ACL`, and `F2FS_FS_SECURITY` control xattrs, ACLs, and LSM label support.
- `F2FS_CHECK_FS` enables runtime consistency BUG_ON checks.
- `F2FS_FAULT_INJECTION` enables fault injection paths.
- `F2FS_FS_COMPRESSION` enables file compression, with selectable LZO, LZO-RLE, LZ4, LZ4HC, and ZSTD backends.
- `F2FS_IOSTAT` enables IO statistics through sysfs and tracepoints.
- `F2FS_UNFAIR_RWSEM` enables unfair rwsem behavior when block cgroup IO priority is configured.

## Research Notes
Compression algorithm options select the corresponding kernel compression/decompression libraries. POSIX ACL depends on xattr support and selects `FS_POSIX_ACL`.
