# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.c

## Purpose
Implements zlib CRC-32 computation.

## Key Elements
Supports static CRC tables from `crc32.h` or optional `DYNAMIC_CRC_TABLE` generation. Exposes `get_crc_table()` and `crc32()`, with optimized little-endian and big-endian four-byte-at-a-time variants when `BYFOUR` is available.

## Behavior/Risks
The source warns that dynamic table generation is not protected by a mutex and should be initialized before multi-threaded use. Runtime endian detection dispatches to little/big optimized paths when pointer/integer assumptions match. Null input returns `0`. `MAKECRCH` mode can regenerate `crc32.h`.

## Dependencies
Uses `zutil.h`, optional `limits.h`, optional `stdio.h` in table-generation mode, and the generated `crc32.h` table in normal static-table builds.
