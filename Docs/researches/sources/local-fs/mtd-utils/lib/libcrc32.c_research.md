# File Research: sources/local-fs/mtd-utils/lib/libcrc32.c

## Purpose
Implements the local CRC32 routine used by JFFS2/MTD utilities.

## Key Elements
Contains a 256-entry CRC32 table for polynomial `0xedb88320` and `mtd_crc32()`, which updates an initial CRC value over a byte buffer.

## Dependencies
Only includes `stdint.h`; declared by `include/crc32.h`.

## Behavior/Risks
Straight table-driven CRC implementation. It does not apply final xor or inversion by itself; callers must use the convention required by their on-flash format.
