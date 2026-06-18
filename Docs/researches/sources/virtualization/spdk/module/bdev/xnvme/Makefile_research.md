# File Research: sources/virtualization/spdk/module/bdev/xnvme/Makefile

Builds the xNVMe bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 5`, `SO_MINOR := 0`.
- Compiles `bdev_xnvme.c` and `bdev_xnvme_rpc.c`.
- Produces library `bdev_xnvme`.
- Adds include path `-I$(SPDK_ROOT_DIR)/xnvme/include`.
- Uses blank SPDK map file.
