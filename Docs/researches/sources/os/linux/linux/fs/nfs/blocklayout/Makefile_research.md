# File Research: sources/os/linux/linux/fs/nfs/blocklayout/Makefile

Builds the pNFS block layout driver.

Key rule:
- `obj-$(CONFIG_PNFS_BLOCK) += blocklayoutdriver.o`

Role:
- Compiles the block layout driver module when pNFS block layout support is configured.
