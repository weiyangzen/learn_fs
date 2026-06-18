# File Research: sources/virtualization/qemu/hw/virtio/virtio-pmem.c

## Purpose
Implements the core virtio persistent memory device. It exposes a host memory backend as guest persistent memory and supports guest flush requests through a virtqueue.

## Main Responsibilities
- Defines `VirtIODeviceRequest` for one pmem request, including virtqueue element, backing fd, pmem/vdev pointers, request, and response.
- Handles flush requests by popping a virtqueue element, validating input/output SG presence, obtaining the host memory backend fd, and submitting an asynchronous worker.
- `worker_cb()` performs `fsync()` on the raw backing fd and writes a virtio-endian response status.
- `done_cb()` copies the response into the guest input SG, pushes the virtqueue element, notifies the guest, and frees request state.
- `virtio_pmem_get_config()` reports persistent memory start address and size in `struct virtio_pmem_config`.
- `virtio_pmem_realize()` validates `memdev`, rejects already mapped backends, marks the backend mapped, initializes virtio device ID `VIRTIO_ID_PMEM`, and creates one 128-entry request virtqueue.
- `virtio_pmem_unrealize()` unmarks the backend, deletes the queue, and cleans up virtio state.
- Provides class callbacks to fill QMP memory-device info and return the memory region.

## Properties
- `VIRTIO_PMEM_ADDR_PROP`: guest physical start address.
- `VIRTIO_PMEM_MEMDEV_PROP`: link to a `HostMemoryBackend`.

## Integration Points
- Uses `HostMemoryBackend` and `memory_region_get_fd()` for the actual host-backed storage/memory.
- Uses QEMU thread pool AIO for potentially blocking `fsync()`.
- Exposes `VirtIOPMEMClass` methods used by the PCI wrapper.
- Uses virtio endian helpers for config and response fields.

## Filesystem/Storage Relevance
The flush path is directly storage-relevant: guest persistence requests become host `fsync()` calls on the memory backend fd, making this file the core durability bridge for virtio-pmem.

## Notable Constraints and Risks
- `memdev` is mandatory and must not already be mapped.
- Flush request validation checks only that at least one out and one in SG are present; malformed request contents are not otherwise interpreted in this file.
- `fsync()` errors are collapsed to response value `1`, while success returns `0`.
- Correct durability depends on the backend memory region having a valid fd and host semantics matching persistent-memory expectations.
