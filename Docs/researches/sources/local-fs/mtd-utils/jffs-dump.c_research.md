# File Research: sources/local-fs/mtd-utils/jffs-dump.c

## Purpose
Raw diagnostic dumper for old JFFS filesystem images.

## Key Elements
Defines old JFFS raw inode structures and constants, checksum/endian helper routines, raw inode printing, then scans an image word-by-word for empty, dirty, and magic regions. Optionally filters by inode number and prints names.

## Dependencies
Uses `common.h`, Linux byteorder macros, and direct `pread` over an image file.

## Behavior/Risks
Diagnostic only. Several declared functions are unused leftovers, and scan logic trusts raw inode sizes from the image when advancing offsets.
