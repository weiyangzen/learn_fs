# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/arcname.c

## Purpose

`arcname.c` initializes ARC namespace symbolic links during boot. It maps loader ARC names such as disk, partition, and CD-ROM paths to NT device names, records system partition information, and reassigns `\SystemRoot`.

## Global State

- `IoArcHalDeviceName`: Unicode `\ArcName\...` for the firmware system/HAL partition.
- `IoArcBootDeviceName`: Unicode `\ArcName\...` for the OS boot partition.
- `IoLoaderArcBootDeviceName`: paged copy of the loader boot ARC name.

## ARC Name Creation

- `IopCreateArcNames()`:
  - Builds global HAL and boot ARC Unicode names from the loader block.
  - Copies the loader boot ARC name.
  - Detects single-disk mode from loader ARC disk-signature list, except when booting from CD-ROM.
  - Handles remote boot by mapping the boot ARC name to `\Device\LanmanRedirector` and storing system partition information.
  - Calls disk ARC creation first, then CD ARC creation if the boot device was not found.
- `IopCreateArcNamesCd()`:
  - Enumerates CD-ROMs through device-interface symbolic links when available, with fallback to `\Device\CdRomN`.
  - Locates the loader ARC signature matching the boot device.
  - Reads 2048 bytes at offset `0x8000`, computes checksum, and matches against the loader checksum.
  - Creates the boot ARC symlink to the matching CD-ROM device.
- `IopCreateArcNamesDisk()`:
  - Enumerates disks through device-interface symbolic links when available, with fallback to `\Device\HarddiskN\Partition0`.
  - Queries storage device numbers and disk geometry.
  - Reads drive layout with `IoReadPartitionTableEx()`.
  - Handles EZ-Drive MBR offset adjustment via `HalExamineMBR()`.
  - Reads the first sector and computes checksum.
  - Matches loader ARC disk signatures against MBR signatures or GPT disk GUIDs, with a single-MBR-disk shortcut.
  - Creates ARC symlinks for whole disks and each partition.
  - Marks `FoundBoot` when the generated partition ARC name matches the loader boot ARC name.
  - Stores system partition information when the generated ARC partition matches the loader HAL/system ARC name.

## SystemRoot and Signature Helpers

- `IopReassignSystemRoot()`:
  - Opens the current boot ARC symbolic link.
  - Queries its NT target.
  - Replaces `\SystemRoot` with a permanent symbolic link to the resolved NT target plus loader boot path.
  - Returns the NT boot path prefix through `NtBootPath`.
- `IopVerifyDiskSignature()`:
  - Rejects invalid loader partition tables.
  - For MBR layouts, compares the MBR signature.
  - For GPT layouts, compares the loader GPT signature GUID with the disk layout GUID.

## Important Details

- The code accommodates both "enabled" disks/CD-ROMs already exposed by MountMgr-style interfaces and fallback legacy device names.
- Some CD boot failure paths intentionally return success because the later boot process can tolerate absent matches in certain Microsoft-compatible cases.
- Duplicate-signature warning exists when partition table/signature match but checksum differs.
- Most functions are `INIT` code except `IopVerifyDiskSignature()`.

## Research Notes

This file is boot-storage glue. For filesystem research, it explains how early boot partition names become stable NT object-manager symbolic links that later filesystem mounts can consume.
