# File Research: sources/local-fs/mtd-utils/include/crc32.h

## Purpose
Declares the local MTD CRC32 routine.

## Key Elements
Includes `stdint.h` and declares `uint32_t mtd_crc32(uint32_t val, const void *ss, int len)`.

## Dependencies
Implemented by `lib/libcrc32.c`.

## Behavior/Risks
The caller controls the initial CRC value; this project commonly passes `0` for JFFS2 node CRCs and uses other constants for UBI/UBIFS elsewhere.
