# File Research: sources/virtualization/spdk/module/bdev/delay/vbdev_delay_rpc.c

This file exposes runtime JSON-RPC methods for delay vbdevs. `bdev_delay_create` decodes base name, virtual name, optional UUID, and four latency values, calls `create_delay_disk()`, and returns the delay bdev name. `bdev_delay_delete` decodes `name`, calls `delete_delay_disk()`, and reports result asynchronously from the unregister callback.

`bdev_delay_update_latency` decodes delay bdev name, latency type through the generated enum decoder, and new latency in microseconds. It maps `-ENODEV` to invalid params, `-EINVAL` to invalid request, treats any other nonzero return as unreachable, and returns boolean success. All generated RPC contexts are freed in cleanup blocks.
