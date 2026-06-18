# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_idxd.c

Registers Intel IDXD/DSA/IAA devices with SPDK's PCI layer.

Important behavior:
- Defines Intel-vendor IDs for DSA, DSA3, IAA, and IAA3 devices.
- Exposes `spdk_pci_idxd_get_driver()` around `spdk_pci_get_driver("idxd")`.
- Registers with `SPDK_PCI_DRIVER_NEED_MAPPING`.

Filesystem/storage relevance: IDXD devices can accelerate data movement and checksum/copy paths used by SPDK storage services.
