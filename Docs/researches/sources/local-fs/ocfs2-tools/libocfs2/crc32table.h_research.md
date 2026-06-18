# File Research: sources/local-fs/ocfs2-tools/libocfs2/crc32table.h

Generated CRC32 lookup-table header used by `blockcheck.c`.

It defines endian-aware `tole()` and `tobe()` macros based on `__BYTE_ORDER`, then provides static 256-entry `crc32table_le` and `crc32table_be` arrays. Values are generated from Linux kernel CRC table generation logic and stored in host-appropriate byte order through compile-time byte swapping.

There are no functions or mutable state. The header is intentionally included directly by the CRC implementation.
