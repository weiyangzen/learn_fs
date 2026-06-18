# File Research: sources/local-fs/mtd-utils/ftl_check.c

## Purpose
Inspects an FTL-formatted MTD character device and prints erase-unit allocation information.

## Key Elements
Finds a plausible FTL erase-unit header, prints formatted size and erase-unit size, scans each erase unit, checks header consistency, identifies transfer units, reads BAM entries, and counts control/data/free/deleted blocks.

## Dependencies
Uses `mtd/mtd-user.h`, `mtd/ftl-user.h`, `mtd_swab.h`, and `common.h`.

## Behavior/Risks
Read-only diagnostic. It assumes classic FTL layout and validates only enough fields to choose a header.
