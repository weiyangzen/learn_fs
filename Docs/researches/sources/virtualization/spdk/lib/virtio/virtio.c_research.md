# File Research: sources/virtualization/spdk/lib/virtio/virtio.c

## Purpose
Implements transport-independent virtio device and split-virtqueue management for SPDK initiator/client-side virtio devices.

## Key Elements
Queue initialization allocates `struct virtqueue`, asks backend ops for queue size and setup, initializes vring memory, links descriptors into a free chain, resets request bookkeeping, and suppresses backend interrupts with event-index or `VRING_AVAIL_F_NO_INTERRUPT`.

Device lifecycle functions construct/destruct a `virtio_dev`, reset a device through ACKNOWLEDGE/DRIVER/feature negotiation, start queues and set DRIVER_OK, stop by resetting status and freeing queues, and delegate config/status/features/queue setup to backend ops.

Feature negotiation intersects requested features with host features, calls backend `set_features`, sets `FEATURES_OK`, and verifies the device accepted it. `virtio_dev_reset` always requests `VIRTIO_F_VERSION_1`.

Request construction uses `virtqueue_req_start`, `virtqueue_req_add_iovs`, `virtqueue_req_flush`, and `virtqueue_req_abort`. I/O vectors are split into descriptors as needed, using virtual addresses for software backends and physical addresses for hardware backends. `finish_req` publishes descriptor chains to the avail ring with memory barriers and increments finished request count. Flush decides whether to notify the backend based on event-index or used-ring no-notify flags.

Completion polling uses `virtio_recv_pkts` and `virtqueue_dequeue_burst_rx` to consume used entries, return cookies and lengths, free descriptor chains, and clear cookies. Queue ownership APIs let SPDK threads acquire, find, query, and release queues under a device mutex.

## Dependencies
Depends on SPDK env/util/barrier/string APIs and `spdk_internal/virtio.h` for virtio structs, ops, vring definitions, and constants.

## Behavior/Risks
This file implements split virtqueues only. It assumes queue sizes are nonzero powers of two. Descriptor allocation reserves up to `2 * iovcnt` descriptors because one iovec can split across physical boundaries for hardware devices. Hardware mode asserts that `spdk_vtophys` succeeds for every descriptor segment.

Interrupt suppression is deliberate: the library is polling-oriented and sets used-event to values intended to avoid interrupts. Queue ownership checks are mutex-protected, but actual queue I/O is expected to run on the owning SPDK thread.
