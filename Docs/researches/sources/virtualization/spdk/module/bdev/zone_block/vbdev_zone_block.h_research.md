# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.h

Declares the public interface for the zone block virtual bdev module.

Key elements:
- `vbdev_zone_block_create()` creates a zoned virtual bdev over a named base bdev with zone capacity and optimal open zone count.
- `vbdev_zone_block_delete()` unregisters a named virtual bdev asynchronously through an SPDK bdev unregister callback.

Dependencies:
- Includes SPDK bdev and bdev module headers for callback and bdev types.

Research notes:
- This header is intentionally narrow; RPC code is the primary local consumer.
