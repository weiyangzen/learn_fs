# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_device.c

Read completely: 89 lines.

This implements PCI configuration-space access for a specific PCI device file descriptor. `pcidev_conf_read` calls `PCI_IOC_CFGREAD` for a register and returns the value; `pcidev_conf_write` calls `PCI_IOC_CFGWRITE`.

Security/reliability notes: range and permission checks are delegated to the kernel. The read function requires a non-null output pointer.
