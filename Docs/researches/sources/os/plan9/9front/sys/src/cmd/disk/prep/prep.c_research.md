# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/prep.c

## Purpose
Implements `disk/prep`, the editor for Plan 9 partition tables stored in sector 1 of a Plan 9 partition.

## Key Behavior
- Opens a disk, optionally overrides sector size, checks that sector 1 is not a FAT boot sector, and reads an existing text partition table unless blank mode is selected.
- Uses the shared editor with sector units and simple partition names, rejecting control characters, `/`, and NUL-like bytes in names.
- Reads/writes lines of the form `part name start end` from/to one sector at disk sector 1.
- Saves the original sector and original in-kernel partitions so failed writes can be restored.
- Supports automatic subpartition layouts selected with repeated `-a partname`, using weighted allocation plus min/max constraints for known names such as `9fat`, `nvram`, `fscfg`, `fs`, `fossil`, `arenas`, `isect`, `bloom`, `swap`, and cache variants.
- Aligns automatic partitions to physical-sector stride using disk physical alignment metadata.
- Prevents non-`9fat` partitions from overlapping the Plan 9 boot sector/partition-table area at the start of the region.
- Writes the new text table and calls `ctldiff()` to update the live Plan 9 disk partition namespace.

## Interfaces And Dependencies
- Uses `edit.c` callbacks for add/delete/write/summary/name checks.
- Uses `<disk.h>` for `Disk`, sector size, physical sector size, offset, and alignment metadata.
- Uses the kernel disk `ctl` file through `ctldiff()`.

## Notes
The FAT boot-sector guard protects users from accidentally running `prep` on a whole FAT-containing disk instead of a Plan 9 partition. Automatic layout allocation is order-sensitive because the `autox` array is also the desired on-disk order.
