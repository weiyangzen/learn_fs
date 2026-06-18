# File Research: sources/virtualization/spdk/module/bdev/daos/bdev_daos_rpc.c

This file provides runtime JSON-RPC methods for DAOS bdevs. `bdev_daos_create` decodes required `name`, `pool`, `cont`, `num_blocks`, and `block_size`, plus optional `uuid` and `oclass`, then calls `create_bdev_daos()` and returns the registered bdev name. `bdev_daos_delete` decodes `name`, calls `delete_bdev_daos()`, and completes asynchronously from the unregister callback.

`bdev_daos_resize` decodes `name` and `new_size`, calls `bdev_daos_resize()`, and returns boolean success. Decode failures use parse or internal error responses depending on the method, and all generated RPC context allocations are freed on cleanup paths.
