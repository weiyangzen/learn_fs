# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/Makefile

## Role

This Makefile builds the pNFS flexfiles layout driver module.

## Build Rules

When `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled, it builds `nfs_layout_flexfiles.o`.

That object is composed of:
- `flexfilelayout.o`
- `flexfilelayoutdev.o`

## Integration

This is only the build declaration for the flexfiles layout driver. The implementation files are outside this work item.
