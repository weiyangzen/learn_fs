# File Research: sources/os/linux/linux-stable/fs/nilfs2/sysfs.h

## Purpose
Declares NILFS2 sysfs support types and attribute-generation macros used by `sysfs.c`.

## Main Contents
- `NILFS_ROOT_GROUP_NAME` is `"nilfs2"`.
- `struct nilfs_sysfs_dev_subgroups` embeds kobjects and completion objects for per-device child groups:
  - `superblock`
  - `segctor`
  - `mounted_snapshots`
  - `checkpoints`
  - `segments`
- Attribute wrapper struct macros:
  - `NILFS_KOBJ_ATTR_STRUCT(name)` for plain kobject attributes.
  - `NILFS_DEV_ATTR_STRUCT(name)` for per-device attributes receiving `struct the_nilfs *`.
  - `NILFS_CP_ATTR_STRUCT(name)` for checkpoint/snapshot attributes receiving `struct nilfs_root *`.

## Macro API
- Attribute declaration helpers:
  - `NILFS_INFO_ATTR`
  - `NILFS_RO_ATTR`
  - `NILFS_RW_ATTR`
- Group-specific aliases:
  - `NILFS_FEATURE_*`
  - `NILFS_DEV_*`
  - `NILFS_SEGMENTS_*`
  - `NILFS_MOUNTED_SNAPSHOTS_*`
  - `NILFS_CHECKPOINTS_*`
  - `NILFS_SNAPSHOT_*`
  - `NILFS_SUPERBLOCK_*`
  - `NILFS_SEGCTOR_*`
- Attribute-list helpers produce pointers for `struct attribute *` arrays.

## Dependencies
Includes `<linux/sysfs.h>`. It forward-uses `struct the_nilfs` and `struct nilfs_root` through callback signatures supplied by including C files and NILFS headers.

## Research Notes
This header centralizes the repetitive sysfs boilerplate. It intentionally keeps typed callback signatures separate by group so that the implementation in `sysfs.c` can recover the owning NILFS object through the proper container object.
