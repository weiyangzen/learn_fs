# File Research: sources/os/plan9/9front/sys/src/9/pc/usbehci.h

## Role

Shared EHCI host-controller definitions for the PC USB 2.0 driver.

## Main Interfaces

- Defines debug print macros tied to `ehcidebug` and endpoint debug flags.
- Declares controller-related opaque types and core structures used by EHCI implementation files.
- Declares `ehcilinkage()`, `ehcimeminit()`, and `ehcirun()`.

## Key Contents

- EHCI capability, operational, status, interrupt, command, port-status, and debug-port bit definitions.
- Typed link constants for iTD, QH, siTD, and FSTN schedule entries.
- Hardware register structures:
  - `Ecapio`: capability registers.
  - `Edbgio`: EHCI debug port registers.
  - `Eopio`: PC operational registers including command/status/intr/frame-list/config/portsc.
- `Ctlr` structure tracks PCI/MMIO identity, operational registers, frame list, async QH list, periodic tree, isochronous state, interrupt counters, DMA allocation hooks, and polling state.

## Dependencies And Assumptions

- Depends on Plan 9 USB endpoint structures and PC PCI/MMIO conventions.
- Operational register layout is PC-specific and assumes EHCI MMIO register spacing.
- 64-bit-capable controller support exists as a register bit, but high address handling is mostly delegated to implementation.

## Research Notes

- This header is the main hardware contract for EHCI code in this directory and `../port` USB code.
- It combines generic EHCI constants with PC-specific operational register mapping.
