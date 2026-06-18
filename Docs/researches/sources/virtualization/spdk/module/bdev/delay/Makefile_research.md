# File Research: sources/virtualization/spdk/module/bdev/delay/Makefile

This makefile builds the `bdev_delay` module from `vbdev_delay.c` and `vbdev_delay_rpc.c`. It sets shared-library version `8.0`, adds `-I$(SPDK_ROOT_DIR)/lib/bdev/` to CFLAGS, uses the blank SPDK map file, and includes SPDK library rules.

The module is always included by the parent bdev makefile, so delay vbdev support is part of the default bdev module set.
