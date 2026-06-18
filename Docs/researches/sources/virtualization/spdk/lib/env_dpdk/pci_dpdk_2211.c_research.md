# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2211.c

Implements `dpdk_fn_table` for DPDK 22.11-style private PCI structures.

Important behavior:
- Includes 22.11 private bus/PCI driver headers.
- Mirrors the 22.07 implementation for resource lookup, device metadata, config read/write, driver registration, interrupt operations, and bus/device helpers.
- Defines compile-time traps for newer APIs such as `rte_pci_mmio_read`, `rte_pci_mmio_write`, and `rte_pci_pasid_set_state`, requiring a new compat layer if SPDK begins using them.
- Used by `pci_dpdk.c` for DPDK 22.11 and later versions deemed ABI-compatible.

Compatibility role: this is the primary function table for modern supported DPDK versions in this source snapshot.
