# File Research: sources/local-fs/mtd-utils/jffs2dump.c

## Purpose
Dumps and optionally endian-converts binary JFFS2 images.

## Key Elements
Parses image endian, content dumping, endian conversion output, CRC recalculation, and NAND data/OOB peeling options. `do_dumpcontent()` walks JFFS2 nodes, validates header/node/data/name/summary CRCs, and prints node details. `do_endianconvert()` writes a byte-swapped image with optional recalculated CRCs.

## Dependencies
Uses `mtd/jffs2-user.h`, `summary.h`, `crc32.h`, `common.h`, endian/byteswap headers, and full-file in-memory loading.

## Behavior/Risks
Global state and fixed `cnvfile[256]` are used. Option table marks `--recalccrc` as requiring an argument while short `-r` does not. Conversion logic handles many node types but has fragile manual pointer arithmetic.
