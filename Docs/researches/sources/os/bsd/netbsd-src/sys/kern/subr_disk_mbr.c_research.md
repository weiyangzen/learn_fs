# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_mbr.c

## Summary
Implements MBR-aware disklabel discovery and writing, including NetBSD partition labels, DOS partition import, extended partitions, protective MBR rejection, ISO/UDF fallback, and optional bad-sector table loading.

## Main Responsibilities
- Reads sectors through common disk sector helper into a reusable buffer.
- Scans primary and extended MBR partition tables.
- Detects and skips protective GPT MBRs and Ontrack DM6 DDO redirection.
- Finds NetBSD labels inside NetBSD or compatible 386BSD partitions.
- Imports MBR partitions into disklabel slots when no NetBSD label is found.
- Scans ISO/UDF Volume Recognition Sequences when neither label nor MBR data yields a label.
- Validates labels across a three-sector scan window and optionally handles endian-swapped labels.
- Writes or updates labels in NetBSD MBR partitions and/or the disk start.

## Important Behavior
`scan_mbr()` tracks extended partition bases, verifies partitions do not exceed `d_secperunit`, records whether a valid MBR exists, and stops on scan errors or found labels. Main MBR partitions are installed into `e` through `h`; extended partitions start at later slots and duplicate entries are avoided.

`validate_label()` scans for disklabel magic and checksum, converts endian-swapped labels when configured, calls `convertdisklabel()` on reads, and writes at the architecture default location if asked to create a missing label.

`scan_iso_vrs()` checks MMC sessions when available, otherwise the start of disk, and marks partition `a` as `FS_ISO9660` when ISO media is detected.

## Dependencies
Uses MBR structures, disklabel helpers, CD/MMC ioctls, UDF/ECMA identifiers, endian helpers, `geteblk()`, buffer I/O, and optional compatibility/config macros.

## Risks
MBR sector addresses are limited to 32-bit fields. Writing labels on disks with multiple NetBSD MBR partitions intentionally updates all matching partitions. The file notes possible MAXPARTITIONS compatibility issues when writing labels to disks with older eight-partition layouts.
