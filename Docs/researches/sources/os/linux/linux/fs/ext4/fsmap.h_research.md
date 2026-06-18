# File Research: sources/os/linux/linux/fs/ext4/fsmap.h

Declares ext4’s internal fsmap structures, formatter callback type, query entry point, and owner constants.

Key behavior:
- `struct ext4_fsmap` stores device, flags, physical block, owner, length, and list linkage.
- `struct ext4_fsmap_head` stores input/output flags, count/entry counters, and low/high keys.
- Declares conversion helpers:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Declares `ext4_getfsmap()`.
- Defines query callback return values:
  - `EXT4_QUERY_RANGE_ABORT`
  - `EXT4_QUERY_RANGE_CONTINUE`
- Defines special owner values for free space, unknown owners, filesystem metadata, journal log, inodes, group descriptors, reserved GDT, block bitmap, and inode bitmap.

Important interactions:
- Used by `fsmap.c` and ioctl-facing code to translate ext4 physical-space records into generic fsmap output.
