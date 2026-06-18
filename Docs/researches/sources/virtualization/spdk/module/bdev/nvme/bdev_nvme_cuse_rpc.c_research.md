# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_cuse_rpc.c

This file exposes NVMe CUSE device registration through JSON-RPC when the build includes CUSE support. It registers `bdev_nvme_cuse_register` and `bdev_nvme_cuse_unregister`.

Both RPCs decode a controller `name`, look up the internal `nvme_ctrlr` with `nvme_ctrlr_get_by_name()`, and call the NVMe library CUSE API on the underlying `spdk_nvme_ctrlr`. Register calls `spdk_nvme_cuse_register()`, and unregister calls `spdk_nvme_cuse_unregister()`.

Responses are boolean on success and JSON-RPC errors on decode failure, missing controller, or CUSE API failure. The file does not own CUSE implementation details; it is a thin RPC adapter whose availability is controlled by the `CONFIG_NVME_CUSE` Makefile flag.
