# File Research: sources/local-fs/mtd-utils/nftldump.c

## Purpose
Inspects and optionally reconstructs data from NFTL partitions.

## Key Elements
Scans eraseblocks for `ANAND` media headers, reads the bad-unit table, reads unit control information from OOB, builds a virtual unit chain table, reports erase unit state, and can write a reconstructed linear output image by selecting the latest valid sector in each virtual chain.

## Dependencies
Uses raw MTD geometry and OOB reads, `mtd/nftl-user.h`, endian helpers, and POSIX I/O.

## Behavior/Risks
Hard-codes `ERASESIZE` as `0x2000` in reconstruction paths and uses fixed-size `UCItable` storage sized for a 40 MiB layout. Suitable for legacy NFTL diagnostics, not general NAND translation layers.
