# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/Makefile

Build rules for the pNFS block layout driver.

Key behavior:
- Builds `blocklayoutdriver.o` when `CONFIG_PNFS_BLOCK` is enabled.
- Driver objects are `blocklayout.o`, `dev.o`, `extent_tree.o`, and `rpc_pipefs.o`.
- The file in this group, `blocklayout.c`, depends on device resolution, extent tree, and pipefs support from the sibling objects.
