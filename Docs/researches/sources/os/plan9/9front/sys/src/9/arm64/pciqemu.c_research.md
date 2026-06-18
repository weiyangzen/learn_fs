# File Research: sources/os/plan9/9front/sys/src/9/arm64/pciqemu.c

QEMU ARM64 PCI ECAM configuration and simple interrupt fanout.

Key behavior:
- Maps PCI ECAM space at `0x3F000000`.
- Implements 8/16/32-bit PCI config reads and writes by ECAM address calculation.
- Registers handlers in a fixed 32-entry vector table.
- Enables four PCI interrupt lines and fans every interrupt to all registered handlers.
- Scans bus 0, maps BARs with `pcibusmap`, and optionally prints inventory.

Dependencies:
- Uses Plan 9 PCI helpers and ARM64 interrupt registration.

Research notes:
- Interrupt dispatch does not demultiplex by device interrupt status; registered handlers must tolerate shared interrupt calls.
