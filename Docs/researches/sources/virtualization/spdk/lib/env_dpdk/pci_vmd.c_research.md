# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_vmd.c

Registers Intel VMD PCI controller IDs with SPDK.

Important behavior:
- Matches Intel SKX and ICX VMD device IDs.
- Exposes `spdk_pci_vmd_get_driver()` around `spdk_pci_get_driver("vmd")`.
- Registers with `SPDK_PCI_DRIVER_NEED_MAPPING | SPDK_PCI_DRIVER_WC_ACTIVATE`.

Filesystem/storage relevance: VMD is commonly used to expose/manage NVMe devices behind Intel Volume Management Device controllers.
