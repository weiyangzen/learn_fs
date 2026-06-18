# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c.c

Implements CRC32C and big-endian CRC32 routines reused from kernel-derived/public-domain lineage and relicensed under GPLv2. The exported functions are `ext2fs_crc32c_le` and `ext2fs_crc32_be`.

Algorithm behavior:
- Includes generated/static tables from `crc32c_table.h`.
- Supports selectable bit widths via `CRC_LE_BITS` and `CRC_BE_BITS`, defaulting to 64.
- Uses slicing-by-4 or slicing-by-8 in `crc32_body` for wide table modes.
- Handles byte alignment before word-at-a-time processing.
- Provides bitwise, 2-bit, 4-bit, 8-bit, 32-bit, and 64-bit paths depending on compile-time definitions.
- Converts CRC state to/from CPU endian for wide table processing.

Dependencies: `crc32c_defs.h`, `crc32c_table.h`, `ext2fs.h`, endian macros from bitops.

Unit-test code under `UNITTEST` defines test buffers and expected CRCs for both LE CRC32C and BE CRC32.

Implementation notes:
- `ext2fs_crc32c_le` uses Castagnoli polynomial through `CRC32C_POLY_LE`.
- `ext2fs_crc32_be` uses Ethernet CRC32 polynomial through `CRCPOLY_BE`.
- The function takes a seed and does not force a final xor, leaving policy to callers.
