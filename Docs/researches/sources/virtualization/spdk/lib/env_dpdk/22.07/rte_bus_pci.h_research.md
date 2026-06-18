# File Research: sources/virtualization/spdk/lib/env_dpdk/22.07/rte_bus_pci.h

Vendored DPDK 22.07 PCI bus header. It exposes PCI device and driver internals, PCI bus lists, registration helpers, resource mapping APIs, config-space access, and I/O port access.

Important definitions:
- `struct rte_pci_device` embeds `struct rte_device`, PCI address/id, BAR resources, interrupt handles, driver pointer, SR-IOV VF count, kernel driver type, PCI name, and VFIO request interrupt handle.
- `struct rte_pci_driver` embeds `struct rte_driver`, carries a PCI bus pointer, probe/remove callbacks, optional DMA map/unmap callbacks, id table, and driver flags.
- `struct rte_pci_bus` embeds the generic bus and owns device/driver lists.
- driver flags describe BAR mapping, write combining, reprobe support, link/removal interrupts, keeping mapped resources, and requiring IOVA-as-VA.

The header declares PCI map/unmap/dump, extended capability lookup, bus-master toggling, driver register/unregister, config read/write, and PCI I/O port map/read/write/unmap APIs.
