# File Research: sources/os/plan9/plan9/sys/src/9/rb/io.h

RouterBOARD AR7161/MIPS board IO, interrupt, reset, PCI, and SMBus definitions.

Key contents:
- Defines `Mhz`, DUART frequency, CPU interrupt levels, and interrupt-level assignments for PCI, USB, Ethernet, UART/APB, and clock.
- Defines AR7161 reset/watchdog/APB/PCI interrupt/reset register addresses and bit masks.
- Defines `Vctl` interrupt handler descriptor.
- Provides PCI bus encoding helpers, PCI config register offsets/classes, `Pcisiz`, and `Pcidev`.
- Defines PCI vendor IDs used elsewhere.
- Defines PCI/ISA window address helpers.
- Defines SMBus transaction types and `SMBus` structure.

Role:
- Hardware contract for clock/watchdog, interrupt routing, PCI support, Ethernet, USB, UART, and any future SMBus users.

Notable risks:
- Register addresses are hard-coded for this SoC/board.
- `PCIWINDOW` and `ISAWINDOW` are zero, so DMA address translation is assumed identity-like.
