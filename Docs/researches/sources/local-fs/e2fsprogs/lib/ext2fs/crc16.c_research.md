# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.c

Implements table-driven CRC-16 using polynomial `0x8005`. The exported function is `ext2fs_crc16`.

The file contains a 256-entry CRC table and updates the CRC byte by byte. It stores the CRC in `crc16_t`, which is an unsigned int typedef from `crc16.h`, to avoid sign-extension issues observed on PowerPC with `__u16`.

Dependencies: `config.h`, optional `sys/types.h`, `ext2fs/ext2_types.h`, `crc16.h`.

Usage in this group: old group descriptor checksums in `csum.c`.

Implementation notes:
- The function accepts a previous CRC seed so callers can compute incrementally.
- It masks to 16 bits after each step.
