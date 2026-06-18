# File Research: sources/virtualization/spdk/module/bdev/uring/Makefile

Builds the Linux `io_uring` bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 7`, `SO_MINOR := 0`.
- Compiles `bdev_uring.c` and `bdev_uring_rpc.c`.
- Produces library `bdev_uring`.
- Uses blank SPDK map file.

No runtime logic is present.
