# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio.c

Common virtio-over-vfio-user implementation used by the virtio-blk, virtio-scsi, and virtio-fs endpoint models.

Key responsibilities:
- Creates and tears down a vfio-user-backed virtio PCI BAR4 memory region.
- Emulates modern virtio PCI common configuration, ISR access, device-specific config, and notification BAR layout.
- Handles feature negotiation, device status transitions, reset, start, and stop.
- Maps and unmaps guest virtqueue memory using SPDK vfio-user DMA mapping helpers.
- Supports both split and packed virtqueues.
- Parses available descriptors into `vfu_virtio_req` IOV arrays.
- Enqueues used descriptors and triggers IRQs with optional interrupt coalescing.
- Provides attach/detach, memory hot-add/remove handling, PCI reset handling, quiesce support, and vendor capability generation.

Important structures come from `vfu_virtio_internal.h`:
- `vfu_virtio_endpoint`: per endpoint transport state.
- `vfu_virtio_dev`: per attached virtio device state.
- `vfu_virtio_vq`: per virtqueue mapping and ring state.
- `vfu_virtio_req`: per request descriptor and mapped IOV state.

Control flow:
- `vfu_virtio_endpoint_setup()` creates an unlinked file for BAR4, truncates it to the virtio BAR size, mmaps the notification region, stores endpoint ops, and sets default queue count/size.
- `vfu_virtio_attach_device()` allocates the device and request pools for all queues, initializes queue SG storage, gets model-specific supported features, and attaches the device to the endpoint.
- `virtio_vfu_pci_common_cfg()` handles common-config reads/writes, including selected feature pages, queue selection, queue size/vector/enable, queue physical addresses, and device status writes.
- `virtio_dev_enable_vq()` maps descriptor, available, and used rings, initializes ring indices, and sets packed-ring phase state when negotiated.
- `vfu_virtio_dev_process_split_ring()` and `vfu_virtio_dev_process_packed_ring()` pull available descriptors, allocate request objects, map descriptors into IOVs, and dispatch via `virtio_ops.exec_request`.
- `vfu_virtio_finish_req()` decrements outstanding I/O, writes the used-ring entry, and returns the request to its free queue.
- `vfu_virtio_vq_flush_irq()` posts interrupts only when there are used requests, guest notification suppression permits it, and coalescing timing allows it.
- `vfu_virtio_quiesce_cb()` returns busy while outstanding I/O exists and completes quiesce asynchronously through a poller.

Dependencies and integration points:
- Calls into model-specific `vfu_virtio_ops` for feature bits, request allocation/free, request execution, config get/set, and start/stop hooks.
- Uses `spdk_vfu_map_one()`, `spdk_vfu_unmap_sg()`, libvfio-user `vfu_irq_trigger()`, and SPDK endpoint helper APIs.
- Uses Linux virtio headers for PCI and ring layout definitions.
- Exports endpoint/device utility functions used by blk/scsi/fs modules.

Notes:
- Notification BAR accesses are expected to be sparse mmap accesses; direct MMIO read/write to the notification range asserts.
- Queue mapping is retried on memory add and selectively unmapped before memory remove.
- The file contains misspelled exported helper names `virito_dev_*_get_next_avail_req`; callers use those exact symbols.
