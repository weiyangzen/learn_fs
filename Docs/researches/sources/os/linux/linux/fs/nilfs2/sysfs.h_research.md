# File Research: sources/os/linux/linux/fs/nilfs2/sysfs.h

Declares NILFS2 sysfs helper types and macros used by `sysfs.c`.

Main contents:
- Defines root sysfs group name `NILFS_ROOT_GROUP_NAME` as `nilfs2`.
- Defines `struct nilfs_sysfs_dev_subgroups`, holding kobjects and unregister completions for per-device subgroups: `superblock`, `segctor`, `mounted_snapshots`, `checkpoints`, and `segments`.
- Defines attribute wrapper structs for:
  - global feature attributes,
  - per-device and per-device subgroup attributes,
  - per-snapshot attributes.
- Provides macros to declare info/read-only/read-write attributes and to list them in attribute arrays.

Design notes:
- The header abstracts repeated sysfs boilerplate into type-specific macros while keeping show/store callbacks strongly typed to either `struct the_nilfs` or `struct nilfs_root`.
- Attribute mode conventions are `0444` for read-only and `0644` for read-write.
- It forward-relies on `struct the_nilfs` and `struct nilfs_root` declarations from NILFS internals.

Dependencies:
- Kernel `linux/sysfs.h`.
- Used directly by NILFS sysfs implementation and indirectly tied to `the_nilfs.h` kobject fields.

Risk notes:
- `NILFS_SEGMENTS_RW_ATTR(name)` expands to `NILFS_RW_ATTR(segs_info, name)`, unlike the other segment macros. No current code in this group uses it, but it looks like a stale or typo-prone macro.
