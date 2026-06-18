# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_crc32ctable.c

## Role

Build-time generator that prints C source for CRC32/CRC32C lookup tables.

## Main Flow

- Computes little-endian CRC32C rows with `CRC32C_POLY_LE`.
- Computes big-endian CRC32 rows with `CRCPOLY_BE`.
- `output_table()` prints generated static arrays with endian conversion wrappers (`tole`, `tobe`).
- `main()` emits a generated-file header and whichever tables are enabled by `CRC_LE_BITS` / `CRC_BE_BITS`.

## Dependencies

Includes `crc32c_defs.h` for polynomial and bit-width settings.

## Risks / Notes

- The big-endian output path calls `output_table(crc32table_be, LE_TABLE_ROWS, ...)`, which appears suspicious because the table is sized with `BE_TABLE_ROWS`.
- This is not runtime filesystem code; errors affect generated CRC table correctness.
