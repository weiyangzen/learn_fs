# File Research: sources/virtualization/spdk/lib/vhost/vhost_internal.h

## Purpose
Defines private vhost library contracts shared by the vhost core, vhost-user transport, vhost-blk backend, vhost-scsi backend, and virtio-blk transport registry.

## Key Elements
Declares global limits for vhost queues, queue size, SCSI targets, iovec count, batch submissions, event coalescing defaults, and session stop timeouts. Defines common virtio/vhost feature masks and packed-ring flag helpers.

Core data structures are `spdk_vhost_virtqueue`, `spdk_vhost_session`, `spdk_vhost_user_dev`, and `spdk_vhost_dev`. Virtqueue state tracks DPDK vring/inflight data, split/packed indices and phases, per-queue task storage, coalescing counters, interrupt object, and backpointer to the session. Session state tracks DPDK vid, memory table, task count, queue array, negotiated features, stop retry count, and DPDK callback semaphore/response fields.

Backend interfaces are separated into `spdk_vhost_user_dev_backend` for per-session lifecycle hooks and `spdk_vhost_dev_backend` for device-level config, JSON, removal, and coalescing hooks. `enum vhost_backend_type` distinguishes block and SCSI backends.

The header declares descriptor translation and queue helpers for split descriptors, packed descriptors, and inflight descriptors: guest physical to vhost virtual address mapping, available-ring fetch, descriptor-chain traversal, iovec conversion, used-ring enqueue, packed-ring enqueue, interrupt signaling, and packed buffer-id extraction.

Vhost-user functions cover device/session creation, start, unregister, busy checks, foreach-session async iteration, coalescing, memory registration, UNIX socket registration, DPDK compatibility hooks, and vhost-user finalization. Block-specific exports include bdev lookup, I/O channel acquire/release, `virtio_blk_process_request`, and controller create/destroy hooks.

The virtio-blk transport abstraction is declared with `spdk_virtio_blk_transport_ops`, `spdk_virtio_blk_transport`, registry/list types, create/destroy/dump/get APIs, and the constructor-style `SPDK_VIRTIO_BLK_TRANSPORT_REGISTER` macro.

## Dependencies
Uses Linux virtio config definitions, DPDK `rte_vhost`, SPDK bdev/log/util/rpc/config/tree headers, and `spdk_internal/vhost_user.h`.

## Behavior/Risks
This is a private ABI for tightly coupled C modules. Layout assumptions matter: several session structs embed `spdk_vhost_session` as their first field and cast from the base pointer. Queue and iovec maximums gate descriptor validation throughout the block and SCSI backends.

The stop and foreach-session comments document important threading contracts: DPDK callbacks are synchronous but SPDK work is asynchronous, and `vhost_user_session_stop_done` must be called on the session lcore while holding the vhost-user device lock.
