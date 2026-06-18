# File Research: sources/local-fs/mtd-utils/docfdisk.c

## Purpose
Inspects and rewrites INFTL partition tables on DiskOnChip devices.

## Key Elements
Scans the first 10 eraseblocks for an INFTL media header (`BNAND`), reads OOB data, prints partition details, accepts up to four requested partition sizes, rewrites partition metadata, duplicates the media header at `buf + 4096`, erases the header block, restores OOB, and writes pages back.

## Dependencies
Uses MTD ioctls, `mtd/inftl-user.h`, `mtd/mtd-user.h`, and `mtd_swab.h` endian helpers.

## Behavior/Risks
Highly destructive and legacy-specific. It warns that failure while erasing/writing may leave the MediaHeader damaged. Uses global buffer pointers and assumes media-header layout details such as the spare copy at offset 4096.
