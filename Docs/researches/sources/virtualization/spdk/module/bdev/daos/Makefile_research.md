# File Research: sources/virtualization/spdk/module/bdev/daos/Makefile

This makefile builds the `bdev_daos` module from `bdev_daos.c` and `bdev_daos_rpc.c`. It sets shared-library version `5.0`, uses the blank SPDK map file, and includes standard SPDK library rules.

The parent bdev makefile includes this directory only when `CONFIG_DAOS` is enabled, matching the implementation's dependency on DAOS client and DFS headers/libraries.
