# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block_rpc.c

Adds JSON-RPC control for the zone block virtual bdev.

Key elements:
- Registers runtime RPC `bdev_zone_block_create`.
- Decodes `name`, `base_bdev`, `zone_capacity`, and `optimal_open_zones`.
- Calls `vbdev_zone_block_create()` and returns the created name on success.
- Registers runtime RPC `bdev_zone_block_delete`.
- Decodes `name`, calls `vbdev_zone_block_delete()`, and completes the JSON-RPC request from the unregister callback.

Dependencies:
- Uses SPDK JSON-RPC, string/error helpers, generated RPC context free helpers, and `vbdev_zone_block.h`.

Research notes:
- Creation parameters mirror `zone_block_config_json()` output in the implementation file.
