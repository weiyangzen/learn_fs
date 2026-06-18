# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio_rpc.c

Adds runtime JSON-RPC control for AIO fsdev instances.

Key elements:
- Registers `fsdev_aio_create`.
- Decodes `name`, `root_path`, optional xattr, writeback cache, max write, and skip read/write options.
- Seeds RPC defaults from `spdk_fsdev_aio_get_default_opts()`.
- Calls `spdk_fsdev_aio_create()` and returns the fsdev name.
- Registers `fsdev_aio_delete`.
- Calls `spdk_fsdev_aio_delete()` and completes via callback.

Dependencies:
- `fsdev_aio.h`, SPDK JSON-RPC, string helpers, and generated RPC context free helpers.

Research notes:
- RPC option names match config JSON emitted by `fsdev_aio_write_config_json()`.
