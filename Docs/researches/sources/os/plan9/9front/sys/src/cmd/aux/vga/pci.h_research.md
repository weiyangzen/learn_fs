# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.h

Header defining the lightweight PCI abstraction used by the VGA utility.

Key contents:
- Bus type enumeration, including ISA, EISA, MCA, PCI, PCMCIA, NuBus, VLB, VME, and other legacy bus classes.
- `MKBUS` and `BUS*` macros for packing and extracting type/bus/device/function into a TBDF integer.
- PCI config-space register offsets for common header fields, type 0 device BAR/subsystem/ROM fields, and type 1 bridge bus/window fields.
- `Pcidev` structure containing TBDF, vendor/device/revision IDs, six memory BAR descriptors with base and size, interrupt line, class fields, linked-list pointer, and raw config FD.
- Declaration for `vgactlpci(Pcidev *)`.

Notable dependencies:
- Assumes Plan 9 integer typedefs such as `ushort`, `uchar`, `uvlong`, and `vlong`.

Research notes:
- This is a local utility header, not a complete PCI subsystem API.
- Only the fields needed by VGA hardware setup are represented.
