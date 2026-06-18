# File Research: sources/local-fs/mtd-utils/compr_zlib.c

## Purpose
JFFS2 zlib compressor adapter.

## Key Elements
Uses `deflateInit` level 3, partial flushes, and a 12-byte reserved stream ending area. Decompression wraps zlib `inflate`. Registers compressor name `zlib`, type `JFFS2_COMPR_ZLIB`, priority `60`, enabled by default.

## Dependencies
Depends on zlib, `common.h`, `compr.h`, and JFFS2 type definitions. Temporarily renames zlib's `crc32` symbol to avoid conflicts.

## Behavior/Risks
The decompressor ignores the final inflate status and returns success after `inflateEnd`, so corrupt compressed input may not always be surfaced correctly.
