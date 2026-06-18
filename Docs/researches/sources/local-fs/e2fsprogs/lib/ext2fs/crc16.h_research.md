# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.h

Declares the CRC-16 interface and documents the algorithm parameters: width 16, polynomial `0x8005`, initial value 0.

Defines:
- `typedef unsigned int crc16_t`
- `extern crc16_t ext2fs_crc16(crc16_t crc, const void *buffer, unsigned int len)`

Implementation note:
- The unsigned int typedef intentionally avoids platform sign-extension problems with 16-bit integer types.
