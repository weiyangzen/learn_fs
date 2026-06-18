# File Research: sources/local-fs/mtd-utils/nftl_format.c

## Purpose
Formats an MTD device area as NFTL or INFTL media.

## Key Elements
Checks or erases erase zones, optionally reads a device BBT, builds a bad-unit table, selects media header units, writes NFTL `ANAND` or INFTL `BNAND` headers plus spare copies, and writes unit control information into OOB.

## Dependencies
Uses `mtd/mtd-user.h`, `mtd/nftl-user.h`, `mtd/inftl-user.h`, endian helpers, raw OOB ioctls, and direct 512-byte page assumptions.

## Behavior/Risks
Highly destructive and legacy-specific. The code explicitly leaves `UnitSizeFactor != 0xFF` as TODO, assumes 512-byte chunks/OOB layout details, and has minimal recovery if media-header writes fail.
