# File Research: sources/os/plan9/9front/sys/src/9/arm64/io.h

ARM64 QEMU interrupt and bus constants.

Key definitions:
- Defines PPI/SPI bases and interrupt numbers for FIQ, virtual counter, UART, and PCI lines.
- Defines `BUSUNKNOWN`, `PCIWINDOW`, and `PCIWADDR`.

Dependencies:
- Used by interrupt, PCI, clock, and UART code.

Research notes:
- The constants match a narrow QEMU/virt platform target rather than a generic ARM64 board description.
