# File Research: sources/os/bsd/dragonflybsd/sys/sys/pciio.h

Userland ioctl ABI for PCI configuration enumeration and access.

Key responsibilities:
- Defines maximum PCI device name length.
- Defines `pci_getconf_status` and `pci_getconf_flags`.
- Defines `struct pcisel` for domain/bus/device/function selection.
- Defines `struct pci_conf` for PCI device identity, class, revision, driver name, and unit.
- Defines `struct pci_match_conf` and `struct pci_conf_io` for filtered enumeration.
- Defines `struct pci_io` for config register read/write and `struct pci_bar_io` for BAR info.
- Defines ioctl commands for getconf, config read/write, attached query, and BAR query.

Important behavior:
- PCI matching can filter by domain, bus, device, function, driver name/unit, vendor/device, and class.
- `pci_conf_io` supports generation and offset tracking for iterative enumeration and list-change detection.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- User pointers in enumeration structures require careful kernel copyin/copyout.
- PCI domain support is included in selectors and must be preserved for multi-domain systems.
