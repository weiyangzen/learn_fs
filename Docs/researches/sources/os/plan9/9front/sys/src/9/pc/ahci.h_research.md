# File Research: sources/os/plan9/9front/sys/src/9/pc/ahci.h

AHCI/SATA register and in-memory structure definitions for the 9front PC port.

Key contents:
- PCI BAR index for AHCI MMIO.
- AHCI host capability, global-control, CAP2, BIOS handoff, enclosure-management, interrupt-status, SATA error, command, control, and status bit definitions.
- `Ahba` host bus adapter register layout.
- `Aport` per-port MMIO register layout, including command list, FIS base, interrupt, task, signature, SATA control/status/error/active, and FBS fields.
- `Afis` received-FIS memory layout pointers.
- Command-list, command-table, PRDT, ATAPI packet, and FIS structure definitions.
- ATA signature and port state constants.

Research notes:
- This header contains data definitions only; AHCI driver behavior is implemented in corresponding C files elsewhere.
- It is PC-port storage substrate code, within subset A’s OS/block-storage-adjacent scope.
