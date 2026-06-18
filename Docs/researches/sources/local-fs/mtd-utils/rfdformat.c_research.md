# File Research: sources/local-fs/mtd-utils/rfdformat.c

## Purpose
Formats NOR flash for Resident Flash Disk usage.

## Key Elements
Validates the target is NOR flash, rejects devices larger than 32 MiB or smaller than two erase units, erases every eraseblock, and writes the two-byte RFD magic at each block start.

## Dependencies
Uses `mtd/mtd-user.h`, `MEMGETINFO`, `MEMERASE`, POSIX I/O, and getopt.

## Behavior/Risks
Fully destructive across the entire device. It performs only minimal RFD initialization, matching the file’s comment that formatting is just erase plus magic placement.
