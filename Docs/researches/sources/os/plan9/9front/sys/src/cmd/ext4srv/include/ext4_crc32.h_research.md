# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_crc32.h

CRC32/CRC32C API header.

Key behavior:
- Declares classic CRC32 and CRC32C functions.
- Exposes the four-slice CRC32C table `crc32c_tab`.
- Defines endian-aware `ext4_crc32_u` macro for feeding one 32-bit word into the CRC32C calculation.
- Declares `ext4_crc32_init`.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_crc32.c`; used by superblock, group, bitmap, inode, directory, extent, and journal checksum code.

Research notes:
- The word-feed macro mutates the `crc` argument as part of the expression, so callers must pass an lvalue.
