# File Research: sources/os/bsd/openbsd-src/sys/sys/pciio.h

Defines PCI userland ioctl structures for config space, ROM, VPD, and VGA decode/locking operations.

Key contents:
- `struct pcisel`: bus/device/function selector.
- `struct pci_io`: selected config register, access width, and data.
- `struct pci_rom`: ROM length and user buffer.
- `struct pci_vpd_req`: VPD offset/count/data.
- `struct pci_vga`: VGA lock and decode controls.
- VGA lock and decode constants.
- Ioctls `PCIOCREAD`, `PCIOCWRITE`, `PCIOCGETROMLEN`, `PCIOCGETROM`, `PCIOCGETVGA`, `PCIOCSETVGA`, `PCIOCREADMASK`, `PCIOCGETVPD`.

Risk notes:
- Direct PCI config and ROM access is privileged device-control ABI and must validate selectors, widths, and user buffers in implementation code.
