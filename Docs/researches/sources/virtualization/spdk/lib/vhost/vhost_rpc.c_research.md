# File Research: sources/virtualization/spdk/lib/vhost/vhost_rpc.c

## Purpose
Provides JSON-RPC handlers for managing SPDK vhost SCSI controllers, vhost block controllers, controller deletion/querying, interrupt coalescing, and virtio-blk transport creation/querying.

## Key Elements
SCSI RPCs include `vhost_create_scsi_controller`, `vhost_start_scsi_controller`, `vhost_scsi_controller_add_target`, and `vhost_scsi_controller_remove_target`. They decode generated RPC context structures, find controllers under `spdk_vhost_lock` when needed, call the vhost SCSI APIs, and send bool or target-number responses.

Block RPC `vhost_create_blk_controller` decodes controller name, bdev name, optional cpumask, and optional transport, then passes the full params object to `spdk_vhost_blk_construct` so transport-specific options such as `readonly` and `packed_ring` can be decoded by the backend.

`vhost_delete_controller` finds the vhost device and calls `spdk_vhost_dev_remove`. If removal returns `-EBUSY`, it allocates a small retry context and reschedules itself on the current SPDK thread, keeping the JSON-RPC request open until removal succeeds or fails.

`vhost_get_controllers` emits an array of controller objects with name, cpumask, coalescing settings, socket path, session info, and backend-specific JSON from `vhost_dump_info_json`. It supports optional filtering by controller name.

`vhost_controller_set_coalescing` forwards delay base and IOPS threshold to `spdk_vhost_set_coalescing`. `virtio_blk_get_transports` lists one or all registered virtio-blk transports. `virtio_blk_create_transport` creates a transport under the vhost lock.

## Dependencies
Uses SPDK JSON-RPC, log, string, env, SCSI, vhost, bdev, generated RPC autogen structures/free helpers, and `vhost_internal.h`.

## Behavior/Risks
Most invalid input and missing devices are returned as JSON-RPC invalid-params errors, though `vhost_get_controllers` uses an internal-error response for its invalid path. The delete retry path stores the original `params` pointer and relies on the request/params lifetime remaining valid while the message is rescheduled on the SPDK thread.

SCSI target removal is asynchronous: successful initiation does not immediately respond; the completion callback sends the final bool response after target removal finishes.
