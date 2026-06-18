# File Research: sources/virtualization/qemu/hw/virtio/iothread-vq-mapping.c

## Purpose
Implements validation, application, and cleanup for mapping virtqueues to named QEMU `IOThread` objects.

## Key Behavior
- Validates every mapping entry references an existing `IOThread`.
- Rejects duplicate IOThread names in a single mapping list.
- Requires all mapping entries to either specify explicit `vqs` lists or none of them to specify `vqs`.
- For explicit mappings, verifies each virtqueue index is below `num_queues`, is assigned once, and that every queue has an assignment.
- For implicit mappings, assigns virtqueues to IOThreads round-robin.
- Stores the selected `AioContext` for each virtqueue in the caller-provided `vq_aio_context` array.
- Takes an object reference on each mapped IOThread during apply and releases it during cleanup.

## Filesystem/Storage Relevance
This is used by virtio devices that want multiple virtqueues serviced by separate AIO contexts. For storage-heavy devices such as virtio-blk, this determines queue parallelism and thread affinity.
