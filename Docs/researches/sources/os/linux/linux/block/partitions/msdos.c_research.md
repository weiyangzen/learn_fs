# File Research: sources/os/linux/linux/block/partitions/msdos.c

## Summary
Implements DOS/MBR partition parsing, extended partition traversal, and optional subpartition parsing for BSD, Solaris x86, UnixWare, and Minix layouts.

## Main Responsibilities
- Validates MBR `55 aa` signature and boot indicators.
- Avoids claiming AIX and GPT protective disks.
- Emits primary and extended partition entries.
- Traverses linked-list logical partitions inside extended partitions.
- Assigns MBR-derived partition UUID strings.
- Marks Linux RAID MBR partitions.
- Dispatches subtype parsers for known nested disklabel formats.

## Key APIs
- `msdos_partition()`.
- Internal helpers: `parse_extended()`, `parse_bsd()`, `parse_solaris_x86()`, `parse_unixware()`, `parse_minix()`.

## Important Behavior
The extended parser follows EBR links iteratively with a 100-link guard. It handles data entries first, then follows the first extended entry, and applies bounds checks to suspicious third/fourth EBR entries.

A valid FAT boot sector with an invalid boot indicator can be treated as a whole-disk FAT filesystem rather than a partition table. Protective GPT entries cause the MSDOS parser to return 0 so the GPT parser can own the disk.

Primary partitions receive metadata UUIDs formatted from the MBR disk signature and slot number. Logical partitions start at `state->next = 5`.

## Optional Subformats
- Solaris x86 VTOC slices.
- BSD/OpenBSD/NetBSD disklabels.
- UnixWare slices.
- Minix subpartitions.
- AIX delegation when configured.

## Risks
MBR formats are ambiguous with FAT boot sectors and legacy vendor overlays. Extended partition traversal must defend against loops, garbage entries, and out-of-container extents.
