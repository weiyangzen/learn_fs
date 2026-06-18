# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.h

Declares SPDK's DPDK PCI compatibility interface.

Important contents:
- `struct spdk_pci_driver` embeds a fixed `driver_buf[256]` for an `rte_pci_driver`, then stores SPDK driver metadata and enumeration callback state.
- `struct dpdk_fn_table` defines all DPDK ABI-sensitive operations used by `pci.c`.
- Declares wrappers for DPDK PCI resources, config access, interrupt setup, bus scan/probe, and generic device devargs operations.

Risk note: the fixed-size `driver_buf` is guarded by static assertions in version-specific implementation files, so compatibility depends on those assertions matching the selected DPDK headers.
