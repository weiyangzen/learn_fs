# File Research: sources/local-fs/mtd-utils/include/mtd/nftl-user.h

## Purpose
Userspace definitions for NFTL media and OOB metadata.

## Key Elements
Defines NFTL block-control info, unit-control variants, OOB wrapper, media header, max erase zones, erase/fold markers, sector states, and zone states.

## Dependencies
Uses fixed-width integer typedefs supplied by callers.

## Behavior/Risks
Models legacy on-flash structures for DiskOnChip/NFTL tooling; packed structs must match media format exactly.
