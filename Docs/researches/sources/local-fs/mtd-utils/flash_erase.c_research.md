# File Research: sources/local-fs/mtd-utils/flash_erase.c

## Purpose
Erases ranges of MTD eraseblocks, optionally writing JFFS2 cleanmarkers.

## Key Elements
Parses `--jffs2`, `--noskipbad`, `--unlock`, and quiet/help/version options. Uses libmtd to get device geometry, skips bad blocks by default, optionally unlocks each eraseblock, erases with `mtd_erase`, and writes cleanmarkers either to NAND OOB or NOR/main area.

## Dependencies
Uses `common.h`, `crc32.h`, `libmtd.h`, `mtd/mtd-user.h`, and `mtd/jffs2-user.h`.

## Behavior/Risks
Destructive flash operation. It refuses JFFS2 formatting on MLC NAND, but otherwise assumes caller-provided offsets/counts are appropriate. Bad-block skipping can be disabled with `-N`.
