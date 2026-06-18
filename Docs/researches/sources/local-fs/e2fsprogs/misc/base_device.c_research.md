# File Research: sources/local-fs/e2fsprogs/misc/base_device.c

## Purpose
Derives a “base device” name from a partition path so fsck scheduling can avoid running multiple checks against partitions on the same physical disk concurrently.

## Main Behavior
Recognizes and truncates:
- `/dev/md*` to the md base.
- DAC960-style `/dev/rd/cXdY`.
- `/dev/hd*` and `/dev/sd*` disk names.
- Old devfs `ide/.../hostN/busN/targetN/lunN` and `scsi/...` hierarchy.
- devfs `/dev/discs/discN` and `/dev/disks/diskN`.

## Integration
Used by fsck logic through `fsck.h`. A `DEBUG` main can run test vectors from stdin.

## Risks / Notes
Returns `NULL` when it cannot confidently parse the device path.
