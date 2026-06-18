# File Research: sources/virtualization/spdk/module/bdev/zone_block/Makefile

Builds the zone block virtual bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `vbdev_zone_block.c` and `vbdev_zone_block_rpc.c`.
- Produces library `bdev_zone_block`.
- Uses blank SPDK map file.

Only build composition is covered by this file; runtime zone-block behavior is in source files outside this work item.
