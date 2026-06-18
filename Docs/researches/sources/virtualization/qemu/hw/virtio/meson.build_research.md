# File Research: sources/virtualization/qemu/hw/virtio/meson.build

## Purpose
Defines the Meson source sets for QEMU's `hw/virtio` subsystem.

## Key Behavior
- Always includes core virtio bus, config I/O, IOThread virtqueue mapping, `virtio.c`, and QMP support.
- Adds PCI, MMIO, crypto, IOMMU, vhost-vsock common, and vDPA device sources according to Kconfig/build options.
- When vhost support exists, includes common `vhost.c`, `vhost-backend.c`, and `vhost-iova-tree.c`.
- When vhost-user support exists, includes `vhost-user.c`, `vhost-user-base.c`, and optional vhost-user MMIO/PCI device stubs.
- Adds vDPA shadow virtqueue support when `have_vhost_vdpa` is true.
- Separates `virtio_pci_ss` for PCI transport frontends, then folds it into `system_virtio_ss` under `CONFIG_VIRTIO_PCI`.
- Adds stub implementations for builds without full vhost/virtio-md support.

## Filesystem/Storage Relevance
This file determines which virtio storage and filesystem devices are built, including virtio-blk PCI, vhost-user-blk PCI, vhost-user-fs, vhost-scsi, vhost-user-scsi, and vDPA device assignment.
