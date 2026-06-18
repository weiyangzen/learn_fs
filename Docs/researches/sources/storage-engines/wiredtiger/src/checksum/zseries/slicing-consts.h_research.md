# sources/storage-engines/wiredtiger/src/checksum/zseries/slicing-consts.h

## Purpose
This header supplies precomputed slicing-by-8 CRC tables for big-endian s390x checksum support. Only the CRC32C little-endian table is active; several IEEE and big-endian tables are retained under `#if 0` as unused reference material.

## Important APIs, Types, and Functions
The active symbol is `crc32ctable_le[8][256]`, declared `static const unsigned int` and aligned to 128 bytes. It is used by `__wt_crc32c_le` in `crc32-s390x.c` for byte-at-a-time fallback, prealignment, tail handling, and seeded wrapper behavior.

## Control Flow
The file has no executable control flow. Compile-time `#if 0` blocks exclude unused `crc32table_le`, `crc32table_be`, and `crc32ctable_be` tables. The active table is indexed by byte values during CRC accumulation in the C code.

## State and Persistence
The table is immutable static data. It persists only in the binary image. Any constant error would corrupt persistent checksum compatibility across block and log files, so the values are effectively part of WiredTiger's storage contract on s390x.

## Dependencies and Integration Points
It is included by `crc32-s390x.c`. The table values mirror the Castagnoli polynomial behavior used in the generic software checksum table, but are arranged for the s390x little-endian CRC helper.

## Risks and Edge Cases
The header is large and mostly numeric, so accidental edits are hard to review by inspection. Because unused tables are present under `#if 0`, changes to active versus inactive sections can be misleading. Alignment attributes should remain compatible with compilers used for s390x builds.

## Test Signals
Checksum comparison tests against the portable implementation are the best signal. Build warnings around unused static data should stay absent because inactive tables are preprocessor-disabled and the active table is consumed in the same translation unit.
