# File Research: sources/virtualization/spdk/module/bdev/split/Makefile

Builds the split virtual bdev module.

Key settings:
- Includes common SPDK make rules from the module tree root.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `vbdev_split.c` and `vbdev_split_rpc.c`.
- Produces library `bdev_split`.
- Uses SPDK blank map file.

No runtime behavior is defined here.
