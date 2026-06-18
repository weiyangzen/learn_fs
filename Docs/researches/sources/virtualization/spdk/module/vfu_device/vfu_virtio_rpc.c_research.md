# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_rpc.c

Defines JSON-RPC methods for managing vfio-user virtio endpoints and their backing devices/targets.

RPCs:
- `vfu_virtio_delete_endpoint`
  - Decodes `name`.
  - Calls `spdk_vfu_delete_endpoint()`.
  - Returns boolean success or invalid-params error.

- `vfu_virtio_create_blk_endpoint`
  - Decodes `name`, `bdev_name`, optional `cpumask`, optional `num_queues`, optional `qsize`, optional `packed_ring`.
  - Creates a `virtio_blk` vfio-user endpoint.
  - Calls `vfu_virtio_blk_add_bdev()`.
  - Deletes the endpoint on add failure.

- `vfu_virtio_scsi_add_target`
  - Decodes `name`, `scsi_target_num`, `bdev_name`.
  - Calls `vfu_virtio_scsi_add_target()`.

- `vfu_virtio_scsi_remove_target`
  - Decodes `name`, `scsi_target_num`.
  - Calls `vfu_virtio_scsi_remove_target()`.

- `vfu_virtio_create_scsi_endpoint`
  - Decodes `name`, optional `cpumask`, optional `num_io_queues`, optional `qsize`, optional `packed_ring`.
  - Creates a `virtio_scsi` vfio-user endpoint.
  - Applies options through `vfu_virtio_scsi_set_options()`.
  - Deletes the endpoint on option failure.

- `vfu_virtio_create_fs_endpoint`
  - Compiled only under `SPDK_CONFIG_FSDEV`.
  - Decodes `name`, `fsdev_name`, `tag`, optional `cpumask`, optional `num_queues`, optional `qsize`, optional `packed_ring`.
  - Emits a deprecation log for virtio-fs vfio-user support removal in `v26.09`.
  - Creates a `virtio_fs` endpoint and calls async `vfu_virtio_fs_add_fsdev()`.
  - Sends JSON-RPC success response from completion callback.

Dependencies and integration:
- Uses autogen RPC context structs and free helpers from `spdk_internal/rpc_autogen.h`.
- Uses SPDK JSON decoders and JSON-RPC response helpers.
- Calls public entry points declared in `vfu_virtio_internal.h`.

Notes:
- Most errors are reported as `SPDK_JSONRPC_ERROR_INVALID_PARAMS` with `spdk_strerror(-rc)`.
- The fs endpoint RPC completion ignores the `status` argument and always sends success; setup-time synchronous errors still go through the invalid path.
