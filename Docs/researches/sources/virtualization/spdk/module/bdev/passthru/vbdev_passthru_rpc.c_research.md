# File Research: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru_rpc.c

This file registers JSON-RPC methods for the passthru bdev module.

`bdev_passthru_create` decodes `base_bdev_name`, `name`, and optional `uuid`, calls `bdev_passthru_create_disk()`, and returns the passthru name as a JSON string on success. Decode failure is logged and returned as an internal JSON-RPC error; create failure uses the negative SPDK errno code directly and formats the message with `spdk_strerror(-rc)`.

`bdev_passthru_delete` decodes `name`, calls `bdev_passthru_delete_disk()`, and completes asynchronously through `rpc_bdev_passthru_delete_cb()`. The callback returns boolean true on zero bdev errno or a JSON-RPC error with the bdev errno and string.

Both handlers use autogen context cleanup helpers from `spdk_internal/rpc_autogen.h`; no persistent state is held in this file.
