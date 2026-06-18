# File Research: sources/virtualization/qemu/block/export/vhost-user-blk-server.c

## Purpose
Implements QEMU's `vhost-user-blk` block export server. It exposes a QEMU block backend as a virtio-blk device over the vhost-user protocol, using `VuServer`/libvhost-user infrastructure and the shared `VirtioBlkHandler`.

## Main Types
- `VuBlkReq`: request wrapper containing `VuVirtqElement`, `VuServer`, and queue pointer.
- `VuBlkExport`: embeds `BlockExport`, `VuServer`, `VirtioBlkHandler`, optional socket channel pointer, and cached `virtio_blk_config`.

## Request Flow
1. `vu_blk_process_vq()` pops descriptors from a `VuVirtq`.
2. Each request is assigned its server and queue, then run in a coroutine.
3. The server in-flight counter is incremented before coroutine entry.
4. `vu_blk_virtio_process_req()` calls `virtio_blk_process_req()`.
5. On success, `vu_blk_req_complete()` pushes the used descriptor and notifies the queue.
6. On both success and negative handler errors, the server in-flight counter is decremented.

## Virtio/vhost-user Interface
`vu_blk_iface` provides:
- `get_features`: advertises virtio-blk size, segment, topology, block size, flush, discard, write-zeroes, write-cache config, MQ, VERSION_1, indirect descriptors, event index, and vhost-user protocol features. Adds read-only when export is not writable.
- `queue_set_started`: installs or removes queue handler.
- `get_protocol_features`: supports config protocol feature.
- `get_config`: copies cached `virtio_blk_config`.
- `set_config`: only accepts frontend writes to `wce`, then calls `blk_set_enable_write_cache()`.
- `process_msg`: intercepts `VHOST_USER_NONE` disconnect and triggers the device panic handler instead of letting generic processing exit abruptly.

## Creation
`vu_blk_exp_create()`:
- Parses `logical-block-size`, defaulting to 512.
- Parses `num-queues`, defaulting to 1 and rejecting zero.
- Rejects multi-threaded block export mode.
- Initializes `VirtioBlkHandler`.
- Initializes virtio-blk config with capacity, block size, queue count, discard and write-zeroes limits.
- Registers AIO context notifiers and block device ops.
- Starts `vhost_user_server_start()` with provided socket address and queue count.

## Draining and Resize
- `vu_blk_drained_begin()` marks the server quiescing and detaches it from the AioContext.
- `vu_blk_drained_end()` clears quiescing and reattaches.
- `vu_blk_drained_poll()` waits while `co_trip` exists or requests are in flight.
- `vu_blk_exp_resize()` refreshes capacity and sends a config-change message.

## Cleanup
- `vu_blk_exp_request_shutdown()` stops the vhost-user server.
- `vu_blk_exp_delete()` removes AIO context notifiers and frees the handler serial.
