# File Research: sources/os/plan9/plan9/sys/src/9/mtx/io.h

## Role

MTX platform I/O definition header. It defines IRQ/vector numbers, interrupt control structures, bus encoding, EISA/PCI constants, PCI device structures, and PCI window address translation.

This is platform hardware description, not filesystem code.

## Main Contents

- IRQ and vector constants:
  - clock, keyboard, UART, PCMCIA, floppy, LPT, AUX, ATA IRQs
  - `VectorPIC`
- `Vctl`: interrupt handler descriptor with ISR/EOI hooks.
- Bus encoding macros:
  - `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSDF`, `BUSBDF`
- EISA constants.
- PCI config offsets and predefined header fields.
- `Pcisiz` and `Pcidev`.
- PCI translation:
  - `PCIWINDOW`
  - `PCIWADDR`

## Important Behavior

- Provides shared definitions for interrupt controller, PCI, Ethernet, and architecture code.
- Sets PCI window base to `0x80000000`.

## Dependencies And Assumptions

- Assumes `Pcidev` and interrupt vectors align with the MTX board's PC-compatible interrupt layout.
- Assumes PCI memory translation through `PADDR(va)+PCIWINDOW`.

## Notable Risks

- Header constants must match firmware/bridge configuration.
- `Pcidev` is a simplified PCI model compared with fuller ports.
