# File Research: sources/os/plan9/plan9/sys/src/9/kw/io.h

## Role

Kirkwood platform I/O and bus definition header. It defines PCI bus IDs/config registers, Kirkwood SoC physical register addresses, interrupt controller layout, CPU control/status registers, PCIe register maps, and window target/attribute constants.

This is platform hardware description used by drivers, including storage/network/USB drivers.

## Main Contents

- Bus encoding macros:
  - `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`
- PCI config offsets and class/subclass constants.
- `Pcidev` and `Pcisiz` structures.
- Kirkwood address constants:
  - `AddrMpp`
  - `AddrSdio`
  - `Addrpci`
  - `Addrpcibase`
  - `AddrEfuse`
- Interrupt groups and IRQ bit numbers for low, high, and bridge interrupts.
- Register structures:
  - `IntrReg`
  - `CpucsReg`
  - `Pciex`
- MBUS target/attribute constants for DRAM, flash, NAND, SPI, boot ROM, and security SRAM windows.

## Important Behavior

- Provides the constants used by `trap.c`, `sdio.c`, `usbehcikw.c`, PCI code, and board setup.
- Encodes Kirkwood-specific interrupt numbering, including SDIO, USB, SATA, Ethernet, UART, GPIO, PCIe, and RTC interrupt bits.
- Defines cache/L2 and reset-control bit meanings used by platform initialization and reboot.

## Dependencies And Assumptions

- Assumes `PHYSIO` and address-space macros from `mem.h`.
- Assumes little-endian interrupt cause bit numbering as documented in comments.

## Notable Risks

- Hardware register layout definitions are brittle and must match the SoC manual.
- Some PCIe fields are partially modeled, with comments indicating incomplete coverage.
