# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_blk.c

## Purpose
Implements virtio-blk as an SPDK bdev for PCI, vhost-user, and vfio-user transports.

## State
- `struct virtio_blk_dev`: embeds `virtio_dev`, SPDK bdev, and feature flags for readonly, unmap, and flush.
- `struct virtio_blk_io_ctx`: per-I/O virtio request header, optional discard/write-zeroes descriptor, response byte, and iov wrappers.
- `struct bdev_virtio_blk_io_channel`: owns one acquired virtqueue and a poller.

## I/O Path
Read, write, unmap, and flush are converted to virtio-blk requests with an out header, optional payload descriptor, and one response descriptor. Reads acquire a bdev buffer before submission. Completion polling uses `virtio_recv_pkts()` and maps `VIRTIO_BLK_S_OK` to success.

Reset completes immediately as success. Write is rejected if the device is readonly; unmap and flush are conditional on negotiated features.

## Device Initialization
`virtio_blk_dev_init()` reads virtio config for block size, capacity, queue count, max segment size/count, and feature flags. It starts the virtio device, fills bdev geometry/capabilities, registers an I/O device, and registers the bdev.

Transport-specific constructors initialize PCI, vhost-user, or vfio-user virtio devices, negotiate supported features, and call common init.

## Hotplug
`bdev_virtio_pci_blk_set_hotplug()` enables a primary-process-only PCI event listener and poller. The monitor removes devices reported by events and enumerates new virtio-blk PCI devices.

## Dependencies And Risks
Depends on SPDK internal virtio/vhost-user APIs and Linux virtio block headers. Each I/O channel requires exclusive virtqueue acquisition. Queue-count validation prevents zero queues and clamps requested queues to host maximum.
