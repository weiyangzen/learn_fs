# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci.h

Read completely: 69 lines.

This public header declares userland PCI helper APIs. It defines `pcireg_t` as `uint32_t` and prototypes bus-wide config reads/writes, device-file config reads/writes, driver-name lookups, and shared PCI info/printing helpers.

Security/reliability notes: declaration-only file. The APIs operate on file descriptors expected to refer to PCI device/bus nodes.
