# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_ae4dma.c

Registers the AMD AE4DMA PCI driver with SPDK's PCI layer.

Important behavior:
- Defines an AMD-vendor PCI ID table for `PCI_DEVICE_ID_AMD_AE4DMA_3E` and `PCI_DEVICE_ID_AMD_AE4DMA_4E`.
- Exposes `spdk_pci_ae4dma_get_driver()` as a typed accessor around `spdk_pci_get_driver("ae4dma")`.
- Uses `SPDK_PCI_DRIVER_REGISTER(ae4dma, ..., SPDK_PCI_DRIVER_NEED_MAPPING)`.

Filesystem/storage relevance: provides discovery for AMD DMA accelerator devices that SPDK components may use for offloaded data movement.
