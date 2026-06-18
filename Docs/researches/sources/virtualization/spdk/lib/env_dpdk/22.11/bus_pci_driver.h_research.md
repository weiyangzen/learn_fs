# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/bus_pci_driver.h

Vendored DPDK 22.11 internal PCI bus-driver header. It supplies PCI device and PCI driver internals that are no longer present in the public `rte_bus_pci.h`.

It defines PCI kernel-driver kinds, `struct rte_pci_device`, PCI conversion macros, `RTE_PCI_DEVICE`, PCI probe/remove and DMA map/unmap callback types, `struct rte_pci_driver`, driver flags, internal PCI driver register/unregister APIs, and the private `rte_pci_ioport` representation.

Differences from 22.07 include an added `bus_info` string on `struct rte_pci_device`, removal of the explicit `struct rte_pci_bus *bus` member from `struct rte_pci_driver`, and internal annotations for sysfs-path and registration functions.
