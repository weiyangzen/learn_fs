# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_crc32.c

CRC32 and CRC32C implementation, with a standard CRC32 table and a slicing-by-4-style CRC32C table initialized at runtime.

Key behavior:
- `ext4_crc32` computes classic CRC32 over bytes using `crc32_tab`.
- `ext4_crc32c` handles unaligned leading bytes, processes aligned 32-bit words through `ext4_crc32_u`, then handles trailing bytes.
- `ext4_crc32_init` fills the derived CRC32C tables `crc32c_tab[1..3]` once.

Notable dependencies:
- `ext4_crc32_u` is defined inline or as a macro in the CRC header.
- Used throughout metadata checksum support: superblock UUID seed, block/inode bitmaps, group descriptors, inodes, directory tails, htree nodes, and extent blocks.

Research notes:
- The file notes the CRC32 code is based on FreeBSD.
- `crc32c_tab` is global rather than static, likely because the inline word helper references it.
