# File Research: sources/virtualization/spdk/lib/env_dpdk/22.11/rte_bus_pci.h

Vendored DPDK 22.11 public PCI bus API header. It forward-declares PCI device, driver, and I/O port types, then exposes only public PCI operations.

Declared APIs cover PCI BAR resource map/unmap, PCI bus dump, extended capability lookup, bus-master enable/disable, config-space read/write, and I/O port map/unmap/read/write. PCI device/driver structs, driver registration, flags, and helper macros live in the internal `bus_pci_driver.h`.
