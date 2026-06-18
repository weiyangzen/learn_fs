# File Research: sources/local-fs/mtd-utils/doc_loadbios.c

## Purpose
Loads a firmware/BIOS image into a DiskOnChip MTD device, preserving an optional IPL prefix/tail.

## Key Elements
Opens flash and firmware, reads MTD geometry with `MEMGETINFO`, optionally preserves bytes before the requested IPL offset, erases affected eraseblocks, rewrites preserved IPL bytes, then writes firmware in 512-byte chunks padded with `0xff`.

## Dependencies
Uses raw MTD ioctls and `mtd/mtd-user.h`.

## Behavior/Risks
Destructive raw flash writer. It does not enforce the disabled 64 KiB firmware size check and has minimal validation of offset/geometry beyond ioctl success.
