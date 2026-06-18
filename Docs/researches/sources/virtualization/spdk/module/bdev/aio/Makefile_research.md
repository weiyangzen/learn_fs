# File Research: sources/virtualization/spdk/module/bdev/aio/Makefile

This makefile builds the `bdev_aio` shared library/module from `bdev_aio.c` and `bdev_aio_rpc.c`. It sets `SO_VER := 8`, `SO_MINOR := 0`, uses the blank SPDK map file, and includes SPDK library build rules.

On Linux it links against `-laio`, matching the implementation's libaio backend. FreeBSD builds the same module without `-laio`, using the kqueue/aio path compiled in `bdev_aio.c`.
