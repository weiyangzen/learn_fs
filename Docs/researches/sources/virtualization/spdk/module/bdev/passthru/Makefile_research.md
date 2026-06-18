# File Research: sources/virtualization/spdk/module/bdev/passthru/Makefile

This Makefile builds the SPDK passthru bdev module as library `bdev_passthru`.

It sets `SPDK_ROOT_DIR` relative to the module directory, includes `mk/spdk.common.mk`, sets shared object version `8.0`, adds `$(SPDK_ROOT_DIR)/lib/bdev/` to `CFLAGS`, and compiles `vbdev_passthru.c` plus `vbdev_passthru_rpc.c`. The module uses `mk/spdk_blank.map` as its map file and includes `mk/spdk.lib.mk` for the common SPDK library build rules.
