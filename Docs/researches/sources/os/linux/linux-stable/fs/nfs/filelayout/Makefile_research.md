# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/Makefile

## Role

This Makefile builds the pNFS NFSv4.1 file layout driver module when `CONFIG_PNFS_FILE_LAYOUT` is enabled.

## Build outputs

- Adds `nfs_layout_nfsv41_files.o` to `obj-y`/`obj-m` through `obj-$(CONFIG_PNFS_FILE_LAYOUT)`.
- Links the module from `filelayout.o` and `filelayoutdev.o`.

## Integration

The resulting module registers layout type `LAYOUT_NFSV4_1_FILES` from `filelayout.c` and uses device/address helper code from `filelayoutdev.c`.
