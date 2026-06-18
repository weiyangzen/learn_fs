# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/Makefile

## Role

This Makefile builds the pNFS Flex File layout driver module when `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled.

## Build outputs

- Adds `nfs_layout_flexfiles.o` through `obj-$(CONFIG_PNFS_FLEXFILE_LAYOUT)`.
- Links the module from `flexfilelayout.o` and `flexfilelayoutdev.o`.

## Integration

The Makefile is parallel in structure to the file-layout driver Makefile, but targets the NFSv4 flexfiles layout implementation in the sibling `flexfilelayout` directory rather than the fixed file layout code researched in this group.
