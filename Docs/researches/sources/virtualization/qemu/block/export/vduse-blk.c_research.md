# File Research: sources/virtualization/qemu/block/export/vduse-blk.c

## Purpose
Implements QEMU's `vduse-blk` block export driver, exposing a `BlockBackend` as a virtio-blk device through Linux VDUSE. It is a transport frontend around the shared virtio-blk request handler in `virtio-blk-handler.c`.

## Main Types
- `VduseBlkExport`: embeds `BlockExport`, owns `VirtioBlkHandler`, `VduseDev`, queue count, reconnect-log filename, atomic in-flight count, and virtqueue started state.
- `VduseBlkReq`: wraps a popped `VduseVirtqElement` with its `VduseVirtq`.

## Core Flow
1. `vduse_blk_exp_create()` validates export options:
   - `num-queues > 0`
   - `queue-size` power-of-two, greater than 2, within `VIRTQUEUE_MAX_SIZE`
   - `logical-block-size` via `check_block_size()`
   - rejects block export multi-threading.
2. It fills `VirtioBlkHandler` with backend, serial, logical block size, and writability.
3. It builds `virtio_blk_config` including capacity, queue topology, block size, discard and write-zeroes limits.
4. It creates a `VduseDev`, sets a reconnect log file under the temp dir, configures each queue, registers the device fd with the AioContext, adds AIO context notifiers, and installs `BlockDevOps`.
5. Queue kicks are delivered through eventfd handlers. `vduse_blk_vq_handler()` pops requests, increments the in-flight export reference counter, and runs each request in a coroutine.
6. `vduse_blk_virtio_process_req()` delegates request execution to `virtio_blk_process_req()` and, on success, pushes completion and decrements the in-flight counter.

## Draining and Lifetime
- Uses `vduse_blk_inflight_inc()` / `vduse_blk_inflight_dec()` to keep the export alive while requests are running.
- `vduse_blk_drained_begin()` disables queue fd handlers and marks queues stopped.
- `vduse_blk_drained_end()` re-enables queues and injects an eventfd kick to avoid missing reconnect activity.
- `vduse_blk_drained_poll()` waits while `inflight > 0`.
- `blk_set_disable_request_queuing(exp->blk, true)` is important because queued backend requests could prevent the in-flight counter from reaching zero during drain.

## Resize and Config Updates
- `vduse_blk_resize()` updates only the virtio config `capacity` field via `vduse_dev_update_config()`.

## Cleanup
- `vduse_blk_exp_delete()` asserts no in-flight requests, detaches fd handlers, removes AIO notifiers, destroys the VDUSE device, unlinks reconnect log unless destruction returns `-EBUSY`, and frees strings.
- `vduse_blk_exp_request_shutdown()` stops virtqueues.

## Notable Edge Case
- If `virtio_blk_process_req()` returns a negative error, `vduse_blk_virtio_process_req()` frees the request and returns without pushing completion and without calling `vduse_blk_inflight_dec()`. Since the in-flight count was incremented before coroutine entry, malformed requests appear able to leak the in-flight reference. This differs from the vhost-user frontend, which decrements in the error path.
