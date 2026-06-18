# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_drvname.c

Read completely: 84 lines.

This provides driver-name lookup helpers through PCI ioctls. `pci_drvname` looks up the driver for a device/function on the opened bus/device context using `PCI_IOC_DRVNAME`; `pci_drvnameonbus` includes an explicit bus number and uses `PCI_IOC_DRVNAMEONBUS`. Both copy the kernel-returned name with `strlcpy`.

Security/reliability notes: name truncation is possible when caller-provided `len` is too small, but bounded. Ioctl errors are returned as `-1` with `errno` from the kernel.
