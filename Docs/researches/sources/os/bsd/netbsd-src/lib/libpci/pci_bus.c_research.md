# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_bus.c

Read completely: 97 lines.

This implements PCI configuration-space access for a bus/domain file descriptor. `pcibus_conf_read` fills a `pciio_bdf_cfgreg` with bus/device/function/register, calls `PCI_IOC_BDF_CFGREAD`, and returns the value. `pcibus_conf_write` fills the same structure and calls `PCI_IOC_BDF_CFGWRITE`.

Security/reliability notes: it performs no validation of bus/device/function/register ranges, relying on the kernel ioctl layer to enforce validity and permissions.
