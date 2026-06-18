# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.h

## Purpose
Central header for the `mkfs.ubifs` user-space builder.

## Key Elements
Collects libc, Linux, UUID, MTD/UBI, UBIFS, key, LPT, CRC, compression, and device-table interfaces. Defines `PROGRAM_NAME`, debug/error macros, path/name hash table element structures, global `info_`, and prototypes for LEB writing and device-table handling.

## Dependencies
Depends on `mtd/ubifs-media.h`, `libubi.h`, `defs.h`, `crc16.h`, `ubifs.h`, `key.h`, `lpt.h`, `compr.h`, and `common.h`.

## Behavior/Risks
This header deliberately binds the tool to Linux-specific filesystem and MTD APIs. It also enforces compression constant consistency at compile time between mkfs-local compression constants and UBIFS media constants.
