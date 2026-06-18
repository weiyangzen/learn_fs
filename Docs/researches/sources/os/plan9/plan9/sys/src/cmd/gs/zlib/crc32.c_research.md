# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.c

## Purpose
Implements zlib’s CRC-32 checksum calculation, including optional dynamic table generation and optimized word-at-a-time paths.

## Public Surface
- `get_crc_table()`.
- `crc32(crc, buf, len)`.

## Implementation Notes
- Uses polynomial table generation under `DYNAMIC_CRC_TABLE`; otherwise includes generated `crc32.h`.
- Optional `MAKECRCH` mode writes generated CRC tables to `crc32.h`.
- `BYFOUR` enables endian-specific 32-bit processing when a four-byte integer type is available.
- `crc32` initializes with `crc ^ 0xffffffff`, processes bytewise or dispatches to little/big-endian routines, then complements result.
- `crc32_little` and `crc32_big` align input, process 32-byte chunks, then remaining words/bytes.

## Dependencies
Includes `zutil.h`; generated table data is in `crc32.h`.

## Risks and Notes
- Source comments warn `DYNAMIC_CRC_TABLE` is not mutex-protected; callers should initialize before multithreaded use.
- Word-at-a-time paths depend on pointer alignment and endian detection.
- Filesystem relevance: none; checksum primitive.
