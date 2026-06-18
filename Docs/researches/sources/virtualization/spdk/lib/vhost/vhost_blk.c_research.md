# File Research: sources/virtualization/spdk/lib/vhost/vhost_blk.c

## Purpose
Implements SPDK's vhost-user block backend and the reusable virtio-blk request executor. It registers a vhost block controller, opens the backing bdev, exposes virtio-blk configuration/features, processes guest virtqueue descriptors into SPDK bdev I/O, and handles bdev hotremove/resize events.

## Key Elements
Defines `spdk_vhost_blk_dev`, `spdk_vhost_blk_session`, and per-descriptor `spdk_vhost_user_blk_task` wrappers around the shared `spdk_vhost_blk_task`. Feature negotiation starts from `SPDK_VHOST_BLK_FEATURES_BASE`, disables unsupported geometry/config-wce/barrier/SCSI features, and conditionally advertises discard, write-zeroes, flush, read-only, and packed-ring support.

The I/O path is `vdev_worker`/`vdev_vq_worker` -> `process_vq` or `process_packed_vq` -> `process_blk_task`/`process_packed_blk_task` -> `virtio_blk_process_request`. Descriptor setup supports split rings, packed rings, and inflight packed-ring recovery. Completion writes virtio status, enqueues the used descriptor or packed-ring completion, decrements session task count, and signals used rings.

`virtio_blk_process_request` validates the virtio request header/status descriptors, computes payload length, strips `VIRTIO_BLK_T_BARRIER` if present, and dispatches to `spdk_bdev_readv`, `spdk_bdev_writev`, `spdk_bdev_unmap`, `spdk_bdev_write_zeroes`, `spdk_bdev_flush`, or GET_ID string copy. `-ENOMEM` bdev submissions are queued with `spdk_bdev_queue_io_wait` and resubmitted later.

Controller lifecycle is split between generic vhost registration and transport operations. `spdk_vhost_blk_construct` opens the bdev, selects a virtio-blk transport, initializes feature bits, and calls `vhost_dev_register`. The built-in `vhost_user_blk` transport calls `vhost_user_init`/`vhost_user_fini`, creates vhost-user devices, supports `readonly` and `packed_ring` JSON options, forwards coalescing calls, and registers through `SPDK_VIRTIO_BLK_TRANSPORT_REGISTER`.

## Dependencies
Depends on Linux `virtio_blk.h`, DPDK/rte vhost inflight APIs, SPDK bdev, bdev module queue-wait, thread/poller, JSON, cpuset/thread helpers, and the local vhost interfaces in `vhost_internal.h`.

## Behavior/Risks
Request validation is strict: malformed descriptor chains, wrong header/status sizes, zero or non-512-byte I/O payloads, invalid discard/write-zeroes payloads, unsupported request types, read-only writes, and nonzero flush sectors fail with virtio error/unsupported statuses.

Packed-ring processing uses descriptor `buffer_id` rather than request index to choose task slots because packed descriptors can be reused across phases while prior requests remain outstanding. Inflight replay processes resubmit lists in reverse order and updates packed avail phase/index during reconnect.

When the bdev is removed, active sessions switch to no-bdev pollers/interrupt handlers that drain guest requests by returning `VIRTIO_BLK_S_IOERR`; the bdev descriptor is closed only after all sessions have been notified. Resize events send vhost-user config-change notifications to each session.

Session stop is asynchronous. It unregisters pollers/interrupts, waits for `task_cnt` to reach zero and for the vhost-user device lock, times out after the configured retry window, releases bdev I/O channels, frees per-vq task pools, and calls `vhost_user_session_stop_done`.
