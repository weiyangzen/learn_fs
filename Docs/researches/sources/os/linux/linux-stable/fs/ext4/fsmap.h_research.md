# File Research: sources/os/linux/linux-stable/fs/ext4/fsmap.h

This header defines ext4’s internal fsmap types, formatter callback, exported conversion/query prototypes, query callback return codes, and special owner constants.

Major contents:
- `struct ext4_fsmap`: internal block-based mapping record with list linkage, device, flags, physical block, owner, and block length.
- `struct ext4_fsmap_head`: internal query header with input/output flags, requested/filled entry counts, and low/high keys.
- Conversion prototypes:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Formatter type:
  - `typedef int (*ext4_fsmap_format_t)(struct ext4_fsmap *, void *)`
- Main query prototype:
  - `ext4_getfsmap()`
- Query callback return values:
  - `EXT4_QUERY_RANGE_ABORT`
  - `EXT4_QUERY_RANGE_CONTINUE`
- Special owners:
  - Free space, unknown owner, static filesystem metadata, journal log, inode table, group descriptors, reserved GDT, block bitmap, inode bitmap.

Important design points:
- Internal lengths and offsets are in filesystem blocks, not bytes.
- Owner constants intentionally share some generic/XFS fsmap owner values and define ext4-specific metadata classes.
- The list node embedded in `ext4_fsmap` supports temporary sorted metadata lists in `fsmap.c`.
