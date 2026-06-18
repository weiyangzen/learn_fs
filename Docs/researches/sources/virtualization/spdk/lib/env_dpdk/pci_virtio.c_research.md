# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_virtio.c

Registers virtio PCI storage device IDs with SPDK.

Important behavior:
- Matches modern and legacy virtio SCSI and virtio block PCI IDs.
- Exposes `spdk_pci_virtio_get_driver()` around `spdk_pci_get_driver("virtio")`.
- Registers with both `SPDK_PCI_DRIVER_NEED_MAPPING` and `SPDK_PCI_DRIVER_WC_ACTIVATE`.

Filesystem/storage relevance: enables SPDK virtio block/SCSI devices in virtualized environments.
