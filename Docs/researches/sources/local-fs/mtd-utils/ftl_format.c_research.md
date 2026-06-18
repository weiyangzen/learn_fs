# File Research: sources/local-fs/mtd-utils/ftl_format.c

## Purpose
Formats an MTD character device as a legacy FTL partition.

## Key Elements
Builds FTL erase-unit headers, computes transfer units, reserve percentage, BAM offset, formatted size, erases the partition, writes headers, and initializes BAM blocks as control blocks. Options include quiet, confirmation prompt, spare transfer blocks, reserve percent, and boot image size.

## Dependencies
Uses `mtd/mtd-user.h`, `mtd/ftl-user.h`, `mtd_swab.h`, and `common.h`.

## Behavior/Risks
Destructive formatter. It assumes 512-byte logical blocks and classic FTL structures; allocation failures for the BAM buffer are not explicitly checked.
