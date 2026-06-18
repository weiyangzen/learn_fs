# File Research: sources/os/linux/linux-stable/fs/btrfs/fiemap.h

## Purpose

`fiemap.h` is the small public header for Btrfs fiemap support.

## Contents

- Header guard: `BTRFS_FIEMAP_H`.
- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info`.
- Declares:

```c
int btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo,
                 u64 start, u64 len);
```

## Role

This header exposes the fiemap entry point implemented in `fiemap.c` to the rest of the Btrfs inode/file operation code. It has no private structs or inline helpers; all implementation detail stays in `fiemap.c`.
