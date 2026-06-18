# File Research: sources/os/plan9/plan9/sys/src/9/boot/parts.c

Early disk partition table reader for boot.

Key behavior:
- Provides minimal SD unit/partition structs and reads `/dev/sd*/ctl` geometry plus `/dev/sd*/data`.
- Adds partitions by writing `part name start end` to the device ctl file.
- Supports:
  - DOS MBR primary and extended partition tables.
  - Plan 9 partitions inside MBR Plan 9 partitions.
  - Old Plan 9 partition tables on the last or second-to-last sector.
  - Bare Plan 9 partition tables in `data`.
  - El Torito boot image partition on ISO-9660 CDs.
- Honors `partition=new|old` environment preference.
- `readparts()` scans `/dev` for `sd*` devices and calls partition parsing for each.

This is intended to expose partitions early enough for nvram/factotum access before full userland disk tools run.
