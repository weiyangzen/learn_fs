# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/fdisk.c

This file implements an interactive and scriptable DOS/MBR partition table editor.

Key behavior:
- Opens a disk with `opendisk`, computes cylinders from heads/sectors, finds MBR offset including Disk Manager overlay handling, reads primary and extended partition tables, and populates generic `Edit` partitions.
- Supports blanking, auto-adding a Plan 9 partition, writing, printing ctl commands, read-only mode, alternate sector size, and treating input as plain file.
- Defines MBR `Tentry`, `Table`, DOS partition type constants, type-name mapping, and `Dospart`.
- `rdpart` recursively reads extended partition chains and records original tables for recovery.
- `recover` restores original tables and kernel ctl partitions after write failures/fatal exits.
- `autopart` finds the largest suitable free gap and creates an active Plan 9 type `0x39` partition if none exists.
- `plan9print` maps DOS partition types to Plan 9 ctl partition names, deduplicating names.
- Editor extensions:
  - `A name`: set active primary partition.
  - `t name [type]`: set partition type.
  - `R`: restore and exit.
- `wrpart` writes primary and extended partition tables and updates kernel sd ctl state through `ctldiff`.

Safety details:
- Overrides `sysfatal` and `abort` to attempt recovery if writes already happened.
- Tracks original partition tables in `rtab`.
- CHS fields are regenerated and saturated at cylinder 1023.
- Extended partitions are written recursively with `wrextend`.

Notable details:
- Partition editing unit is cylinder; actual MBR fields are sector/LBA.
- New non-primary partitions reserve the first track/sector offset similarly to historical DOS extended layout rules.
