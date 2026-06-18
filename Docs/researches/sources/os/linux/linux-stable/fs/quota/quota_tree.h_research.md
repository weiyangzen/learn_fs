# File Research: sources/os/linux/linux-stable/fs/quota/quota_tree.h

## Purpose
Defines the on-disk data-block header used by the VFS quota tree implementation.

## Key Definition
`struct qt_disk_dqdbheader` contains:
- `dqdh_next_free`: next block with free entries,
- `dqdh_prev_free`: previous block with free entries,
- `dqdh_entries`: valid entry count,
- padding to 16 bytes.

## Constant
`QT_TREEOFF` is `1`, meaning the quota tree root starts at block 1 of the quota file.

## Role
Used by `quota_tree.c` and v2 quota format support to manage leaf/data blocks in quota files.
