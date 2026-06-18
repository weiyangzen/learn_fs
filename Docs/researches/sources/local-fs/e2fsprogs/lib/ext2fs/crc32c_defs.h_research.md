# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c_defs.h

Defines CRC polynomial constants, compile-time table width controls, validation checks, constant byte-swap helper, and branch prediction macros for `crc32c.c`.

Constants:
- `CRCPOLY_LE` / `CRCPOLY_BE`: standard Ethernet CRC32 polynomial.
- `CRC32C_POLY_LE` / `CRC32C_POLY_BE`: Castagnoli CRC32C polynomial.

Configuration:
- `CRC_LE_BITS` defaults to 64.
- `CRC_BE_BITS` defaults to 64.
- Preprocessor checks reject invalid widths; valid values are 1, 2, 4, 8, 32, and 64.

Helpers:
- `___constant_swab32`
- `likely`
- `unlikely`

Implementation notes:
- The header assumes `uint32_t` is available from the includer.
- Wide CRC modes are intended for performance-sensitive code paths.
