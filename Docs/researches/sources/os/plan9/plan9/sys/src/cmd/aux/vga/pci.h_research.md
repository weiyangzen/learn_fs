# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.h

Defines PCI bus encodings, PCI configuration register offsets, and the `Pcidev` structure used by `aux/vga`.

Key contents:
- Bus type enum values, including `BusPCI`.
- `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and `BUSUNKNOWN` macros for Plan 9 TBDF encoding.
- Type 0/type 1 PCI configuration offsets for IDs, command/status, class codes, header type, BARs, interrupt fields, bridge bus numbers, memory/I/O windows, and bridge control.
- `Pcidev` fields for TBDF, vendor/device/revision IDs, six BAR records, interrupt line, class/subclass, flat list link, bridge child link, and same-bus link.

Important details:
- BAR records store both original BAR value and probed size.
- The same struct supports both the recursive bus tree and global flat matching list.

Filesystem relevance:
- Indirect: shared hardware-discovery definitions for VGA controllers.
