# File Research: sources/local-fs/mtd-utils/compr_rtime.c

## Purpose
JFFS2 RTIME compressor adapter implementing a simple byte-history encoder.

## Key Elements
Tracks last positions for each byte value, emits literal byte plus run length pairs, and reconstructs output with overlapping-copy handling. Registers compressor name `rtime`, type `JFFS2_COMPR_RTIME`, priority `50`, enabled by default.

## Dependencies
Uses `stdint.h`, `string.h`, and `compr.h`.

## Behavior/Risks
The decompressor trusts the encoded stream and target `destlen`; malformed input can make it read beyond compressed data because `srclen` is unused.
