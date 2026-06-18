# File Research: sources/local-fs/mtd-utils/include/mtd/ubifs-media.h

## Purpose
Defines UBIFS on-flash format constants and node layouts.

## Key Elements
Declares UBIFS magic/version/minimum sizes, key format constants, inode/file/node/compression enums, filesystem area limits, node size macros, inode flags, common node header, device descriptor, inode, dent, data, truncation, padding, superblock, master, reference, branch, index, commit-start, and orphan node structs.

## Dependencies
Uses Linux endian types from `asm/byteorder.h`.

## Behavior/Risks
This is persistent media ABI. Packed structs and padding sizes are part of disk format and must be kept synchronized with kernel UBIFS.
