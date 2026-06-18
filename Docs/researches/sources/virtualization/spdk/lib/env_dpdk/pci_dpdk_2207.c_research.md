# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2207.c

Implements `dpdk_fn_table` for DPDK 22.07-style private PCI structures.

Important behavior:
- Includes DPDK 22.07 private compatibility headers.
- Static-asserts that `spdk_pci_driver.driver_buf` starts at offset 0 and is large enough for `struct rte_pci_driver`.
- Directly accesses `rte_pci_device` fields such as `mem_resource`, `name`, `device.devargs`, `addr`, `id`, `device.numa_node`, and `intr_handle`.
- Converts SPDK PCI ID tables into DPDK `rte_pci_id` arrays and registers with `rte_pci_register()`.
- Translates SPDK driver flags to `RTE_PCI_DRV_NEED_MAPPING` and `RTE_PCI_DRV_WC_ACTIVATE`.
- Provides interrupt helpers around `rte_intr_*`.

Compatibility role: selected by `pci_dpdk.c` for older supported DPDK versions whose private PCI ABI matches this layout.
