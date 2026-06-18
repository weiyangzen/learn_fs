# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/fdisk.c

## Purpose
Implements `disk/fdisk`, the DOS/MBR partition-table editor, including primary and extended partition chains.

## Key Behavior
- Parses options for auto Plan 9 partitioning, blank mode, file mode, read-only mode, sector-size override, CHS verbosity, print mode, and write mode.
- Uses disk geometry to expose editor units as cylinders while preserving sector offsets for kernel `ctl` commands.
- Reads the MBR signature, recursively reads extended boot records, records recovery copies of every table touched, and rejects GPT protective MBRs with a pointer to `disk/edisk`.
- Models entries as `Dospart`, combining `Part` with raw MBR fields, EBR start/type, and primary-vs-secondary state.
- Auto-partitioning finds the largest usable gap with room in primary slots, creates an active Plan 9 partition if no primary is active, and skips LBA 0/track boot sectors.
- Enforces DOS slot constraints: at most four primary-slot consumers, with secondary partitions represented by extended partition chains.
- Provides fdisk-specific commands: `A` sets the active primary partition, `t` changes the DOS partition type, and `R` restores original partition tables and exits.
- Writes primary entries and nested EBRs, recalculating CHS fields and LBA-relative fields for each table.
- On write failure, restores all saved original table sectors and attempts to restore the kernel partition namespace.
- Prints summaries with changed/active markers, cylinder ranges, byte-scaled sizes, and DOS type names.

## Interfaces And Dependencies
- Uses `edit.c` through an `Edit` callback table for generic command handling and `ctldiff()` for live partition updates.
- Uses `<disk.h>` disk geometry and raw fd/wfd/ctlfd fields.
- Uses Plan 9 FIS constants indirectly only through included disk environment; the MBR format is local to this file.

## Notes
This file treats error recovery as part of the write path: `diskfatal()` invokes `recover()` after any table write has occurred. The code keeps historical CHS compatibility even though LBA fields are the operative values.
