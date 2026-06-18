# File Research: sources/virtualization/qemu/hw/virtio/virtio.c

## Purpose
Core QEMU virtio implementation. This file implements common virtio device and virtqueue behavior shared by virtio transports and devices, including split rings, packed rings, queue notification, DMA mapping, reset/lifecycle handling, migration state, ioeventfd integration, and QMP inspection helpers.

## Main Data Structures
- `VRingDesc`, `VRingAvail`, `VRingUsedElem`, `VRingUsed`: split virtqueue layout.
- `VRingPackedDesc`, `VRingPackedDescEvent`: packed virtqueue layout and event suppression structures.
- `VRingMemoryRegionCaches`: cached guest memory mappings for descriptor, available, and used rings, freed through RCU.
- `VRing`: queue size, alignment, guest physical ring addresses, and region caches.
- `VirtQueue`: per-queue runtime state: vring, used element staging, avail/used indexes and wrap counters, notification state, vector, event notifiers, queue handler, and owning `VirtIODevice`.

## Major Responsibilities
- Maintains `virtio_device_names[]` and maps virtio IDs to stable device names.
- Initializes and refreshes ring memory caches with `virtio_init_region_cache()`, invalidating old mappings through RCU.
- Computes split-ring addresses from descriptor base and alignment in `virtio_queue_update_rings()`.
- Reads/writes split and packed descriptors with endian-aware helpers.
- Implements queue notification enable/disable for split and packed queues, including event index handling and memory barriers.
- Detects queue emptiness and polls for new descriptors.
- Maps guest DMA descriptors into host iovecs, with descriptor validation and cleanup paths.
- Pops, fills, flushes, pushes, rewinds, detaches, and drops virtqueue elements for split, packed, and in-order modes.
- Implements interrupt signaling through ISR bits, guest notifiers, irqfd/deferred notifier paths, and config-change notifications.
- Handles virtio status negotiation, feature validation, reset, queue setup, queue vector lists, and lifecycle hooks.
- Saves and loads legacy and modern virtio migration state, including optional subsections for endian, 64/128-bit features, ringsize, broken/started/disabled flags, packed queues, and transport extra state.
- Registers QOM type `TYPE_VIRTIO_DEVICE` and default class methods.
- Provides QMP experimental inspection APIs for queue status and split-ring queue elements.
- Supplies guarded bottom-half helpers tied to the transport reentrancy guard.

## Key Control Flow
- Device setup: `virtio_init()` allocates queues/config, initializes vectors and default state, and registers VM state change handling.
- Queue creation: `virtio_add_queue()` finds a free queue slot, sets default size/alignment, stores output handler, and allocates `used_elems`.
- Guest queue setup: transport calls address/size setters, which update ring addresses and region caches.
- Descriptor processing: `virtqueue_pop()` dispatches to split or packed pop logic, validates descriptor chains, maps DMA buffers, and advances avail state.
- Completion: device calls `virtqueue_fill()` plus `virtqueue_flush()` or `virtqueue_push()`; the file writes used entries/descriptors, updates indexes, unmaps DMA, and decrements `inuse`.
- Notification: `virtio_notify()` checks event suppression rules and signals the transport vector or notifier.
- Migration: `virtio_save()` and `virtio_load()` preserve queue state, feature state, config, and device-specific data.

## Error Handling and Safety
- Guest mistakes call `virtio_error()`, which marks virtio 1.x devices as needing reset, notifies config, and marks the device broken.
- Descriptor loops, invalid indirect tables, zero-sized buffers, out-of-range heads, bad queue indexes, and failed mappings are detected.
- Memory ordering is explicit around descriptor visibility, event flags, and avail/used indexes.
- Cached guest memory is invalidated after writes and replaced under RCU to avoid use-after-free across readers.
- Migration load validates queue counts, queue indexes, feature compatibility, ring consistency, and in-use arithmetic.

## Filesystem/Storage Relevance
This is the common virtio substrate used by storage-facing devices such as virtio-blk, virtio-scsi, virtio-fs, virtio-pmem, and related vhost/virtio devices. Correct descriptor mapping, completion ordering, notification suppression, and migration restoration are foundational for virtual block and filesystem I/O correctness.

## Notable Details
- Supports both legacy split rings and modern packed rings.
- Supports `VIRTIO_F_IN_ORDER`, `VIRTIO_RING_F_EVENT_IDX`, `VIRTIO_F_NOTIFICATION_DATA` compatibility checks, IOMMU-platform feature validation, and variable legacy vring alignment.
- For packed queues, `last_avail_idx` and `used_idx` include wrap-counter state in packed migration/helper encodings.
- QMP element inspection explicitly rejects packed rings.
