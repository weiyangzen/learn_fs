# File Research: sources/virtualization/spdk/lib/env_dpdk/env_internal.h

Internal env_dpdk header shared by environment initialization, PCI, and memory code. It requires DPDK 21.11 or newer and defines address-space constants for the two-level/three-level memory maps: 256 TB virtual range, 1 GB chunks, and masks.

It declares initialization/finalization hooks for PCI environment, memory registration map, and vtophys map, plus IOMMU DMA BAR map/unmap helpers, PCI-device add/remove notifications for vtophys, and option-driven toggles for hugepage use, vtophys use, and NUMA enforcement.
