# File Research: sources/virtualization/spdk/module/bdev/rbd/Makefile

Builds the SPDK Ceph RBD bdev module.

Key settings:
- Includes SPDK common and library make rules through `SPDK_ROOT_DIR := $(abspath $(CURDIR)/../../..)`.
- Sets shared object version `SO_VER := 9`, `SO_MINOR := 0`.
- Compiles `bdev_rbd.c` and `bdev_rbd_rpc.c`.
- Produces library `bdev_rbd`.
- Uses the blank SPDK map file.

This Makefile is purely build glue and has no runtime logic.
