# File Research: sources/virtualization/spdk/module/bdev/aio/bdev_aio_rpc.c

This file exposes runtime JSON-RPC methods for the AIO bdev. `bdev_aio_create` decodes required `name` and `filename` plus optional `block_size`, `readonly`, `fallocate`, `uuid`, and `nowait`. It calls `create_aio_bdev()` and waits for SPDK bdev examine completion before returning the new bdev name, so callers see a fully examined device.

`bdev_aio_rescan` decodes `name`, calls `bdev_aio_rescan()`, and returns boolean success. `bdev_aio_delete` decodes `name`, calls `bdev_aio_delete()`, and completes the RPC from the async unregister callback. All generated RPC contexts are freed on every path, and errors use SPDK JSON-RPC error responses with `spdk_strerror(-rc)` where applicable.
