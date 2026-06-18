# File Research: sources/local-fs/mtd-utils/flashcp.c

## Purpose
Copies a regular file to an MTD flash device, erasing first and verifying afterward.

## Key Elements
Parses `-v/--verbose`, validates input file fits device size, erases enough eraseblocks, writes data in 10 KiB chunks, rewinds both descriptors, reads both back, and compares.

## Dependencies
Uses raw `MEMGETINFO` and `MEMERASE` ioctls from `mtd/mtd-user.h`.

## Behavior/Risks
Destructive writer. It does not handle bad NAND blocks and contains a compile-time `#warning` noting smaller erase regions are not handled.
