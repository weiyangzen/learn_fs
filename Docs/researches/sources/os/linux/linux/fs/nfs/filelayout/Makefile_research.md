# File Research: sources/os/linux/linux/fs/nfs/filelayout/Makefile

## Role

This Makefile builds the pNFS NFSv4.1 files layout driver module.

## Build Rules

When `CONFIG_PNFS_FILE_LAYOUT` is enabled, it builds `nfs_layout_nfsv41_files.o`.

That object is composed of:
- `filelayout.o`
- `filelayoutdev.o`

## Integration

The module provides the layout driver registered by `filelayout.c` and the device-ID/data-server helpers in `filelayoutdev.c`.
