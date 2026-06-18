# File Research: sources/os/linux/linux/fs/zonefs/Kconfig

## Purpose

Defines the kernel configuration option for zonefs.

## Main Responsibilities

- Adds `CONFIG_ZONEFS_FS`.
- Requires block-layer support and zoned block devices.
- Selects iomap and CRC32 support.
- Describes zonefs as exposing zones of a zoned block device as files.

## Important Invariants

- zonefs cannot be built without `BLK_DEV_ZONED`.
- iomap and CRC32 are required implementation dependencies.

## Dependencies

Kernel Kconfig system, block layer, zoned block device support, iomap, CRC32.

## Research Notes

Build-time entry point for enabling zonefs.
