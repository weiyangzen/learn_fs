# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_ioat.c

Registers Intel IOAT DMA engine PCI IDs with SPDK.

Important behavior:
- Contains a broad Intel IOAT ID table spanning SNB, IVB, HSW, BWD, BDX, SKX, and ICX device IDs.
- Exposes `spdk_pci_ioat_get_driver()` around `spdk_pci_get_driver("ioat")`.
- Registers the driver with `SPDK_PCI_DRIVER_NEED_MAPPING`.

Filesystem/storage relevance: IOAT devices are DMA offload engines used by SPDK for copy/data-movement acceleration.
