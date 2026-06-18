# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_internal.h

Internal shared header for vfio-user virtio device implementations.

Key contents:
- Defines host-supported common virtio features:
  - `VIRTIO_F_VERSION_1`
  - `VIRTIO_RING_F_INDIRECT_DESC`
  - `VIRTIO_F_RING_PACKED`
- Defines the virtio PCI BAR4 layout:
  - common config
  - ISR access
  - device-specific config
  - notifications
- Defines queue and request limits:
  - `VIRTIO_DEV_MAX_IOVS`
  - `VIRTIO_DEV_VRING_MAX_REQS`
  - `VIRTIO_DEV_MAX_VQS`
  - default/max queue sizes.

Important data structures:
- `struct virtio_pci_cfg`: tracks selected feature pages, negotiated guest features, MSI-X config vector, status, config generation, queue selection, and ISR byte.
- `enum vfu_vq_state`: created, active, inactive.
- `struct q_mapping`: stores guest queue DMA mapping, SG entry, physical address, local IOV, virtual address union, and length.
- `struct vfu_virtio_vq`: stores queue identity, size, enable/vector state, ring addresses, mapped queue regions, split/packed ring indices and phases, used request count, and interrupt coalescing timestamp.
- `struct vfu_virtio_dev`: stores device name, queue count, host features, PCI config state, queue array, backpointer to endpoint, and SG storage.
- `struct vfu_virtio_ops`: model-specific callbacks for features, request allocation/free, request execution, config get/set, and device start/stop.
- `struct vfu_virtio_endpoint`: per endpoint common state, including BAR fd, notification mapping, queue defaults, packed-ring flag, coalescing delay, SPDK endpoint/thread, operation table, outstanding I/O, and quiesce poller state.
- `struct vfu_virtio_req`: common request object containing queue/device pointers, used length, split/packed descriptor identifiers, mapped IOVs, writeability flags, indirect descriptor mapping, and SG storage.

Inline helpers:
- Feature check helper.
- Queue desc/avail/used region size calculators for split and packed rings.
- Event suppression check for split and packed queues.
- Device started check.
- Descriptor flag helpers for indirect and writeable descriptors.
- Packed-ring available/used phase tests.
- Request writeability check.
- Alloc/free wrappers around model-specific callbacks.

Exports:
- Common ring enqueue, ring processing, request completion, IRQ flushing, config notification, endpoint setup/destruct, attach/detach, memory add/remove, reset, quiesce, vendor capability, and model-specific public entry points for blk/scsi/fs.

Notes:
- This header is the contract between common virtio transport code and the individual device models.
- It depends on Linux virtio headers and `spdk/vfu_target.h`.
