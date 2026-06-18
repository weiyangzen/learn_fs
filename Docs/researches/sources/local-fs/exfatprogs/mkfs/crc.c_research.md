# File Research: sources/local-fs/exfatprogs/mkfs/crc.c

`crc.c` supplies EFI/GPT CRC32 support for `mkfs.exfat`.

It contains a static little-endian CRC32 table derived from Gary S. Brown’s public-domain table and implements:
- `crc32_le_base()`, a local table-driven little-endian CRC update helper.
- `exfat_efi_crc32()`, the exported wrapper used by GPT construction. It starts with all bits set, processes the buffer, then bitwise-inverts the result, matching common EFI CRC32 behavior.

`mkfs.c` uses this function to compute:
- GPT partition entry array CRC.
- GPT main header CRC.
- GPT backup header CRC.

The file is self-contained apart from project headers and does not allocate memory or perform I/O.
