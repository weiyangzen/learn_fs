# File Research: sources/os/bsd/freebsd-src/sys/sys/pciio.h

This header defines the `/dev/pci` ioctl ABI for userland inspection and limited manipulation of PCI devices. It includes `<sys/ioccom.h>`, defines `PCI_MAXNAMELEN`, and provides selection, match, result, config access, BAR, VPD, mmap, and BAR I/O request structures.

`struct pcisel` identifies a PCI function by domain, bus, device, and function. `struct pci_conf` reports device IDs, class/subclass/progif/revision, driver name/unit, NUMA domain, reported length, bridge bus fields, and spare room for future ABI expansion. `struct pci_match_conf` and `struct pci_conf_io` implement filtered enumeration with generation/offset/status handling.

Other ioctls operate on config registers (`struct pci_io`), BAR metadata (`pci_bar_io`), VPD element lists, BAR mmap setup, and direct BAR read/write (`pci_bar_ioreq`). Ioctl commands include read/write/attached, get BAR, list VPD, BAR mmap, BAR I/O, and get config.

Filesystem relevance is device-node ABI related: this header defines the stable structures used when userland opens a character device and issues ioctls into PCI bus code. It is important for storage controllers and other filesystem-adjacent hardware discovery/configuration.
