# File Research: sources/virtualization/qemu/hw/virtio/vhost-shadow-virtqueue.c

## Purpose
Implements shadow virtqueues that sit between a guest virtqueue and a vhost device, allowing QEMU to relay descriptors and notifications while controlling address translation and migration behavior.

## Key Behavior
- Validates that transport feature bits are compatible with shadow virtqueue operation.
- Tracks free descriptor slots and descriptor chains in an internal split vring.
- Translates HVA-backed or GPA-backed guest buffers through `VhostIOVATree`.
- Writes translated out/in descriptor chains into the shadow vring and updates the shadow avail index with memory barriers.
- Kicks the hardware/backend notifier when event-index or no-notify logic says a kick is needed.
- Forwards guest available buffers until the queue is empty or SVQ descriptor space is exhausted.
- Caches one guest element in `next_guest_avail_elem` when the SVQ is full.
- Reads used elements from the device used ring, validates IDs and descriptor state, returns descriptors to the free list, and recovers the original `VirtQueueElement`.
- Pushes completed elements back to the guest virtqueue and notifies the guest call fd.
- Provides polling for synchronous wait paths.
- Manages guest kick fd, guest call fd, host call handler, shadow vring mmap allocation, and teardown.
- On stop, flushes pending used entries and unpops outstanding guest elements where possible.

## Filesystem/Storage Relevance
Shadow virtqueues are central to vhost-vDPA migration and mediated vhost operation. For storage and virtio-fs style devices, they preserve virtqueue semantics while QEMU remaps guest buffers into backend-visible address spaces.
