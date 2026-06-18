# File Research: sources/os/plan9/plan9/sys/src/9/ppc/imm.h

## Role

Register and data-structure map for the MPC8260 internal memory map, CPM, communication controllers, buffer descriptors, and command encodings.

## Main Definitions

Defines interrupt vector numbers, generic buffer descriptor layout and flags, ring descriptor state, MCC/IOC/SCC/FCC parameter RAM structures, SCC/FCC/SMC/SPI register layouts, memory-controller bank maps, I/O ports, IDMA, parameter-base areas, UART SMC parameter RAM, serial interface registers, and the large `RegMap`/`IMM` layout matching documented offsets.

Also defines `FCCextra`, CPM command register fields, sub-block/page codes, operation codes such as `InitRxTx`, channel IDs like `FCC1ID`, and clock route identifiers.

## Interfaces

Declares global `IMM *imm`, `uartsmcoffset[]`, and low-level helpers `bdalloc`, `cpmop`, `ioplock`, `iopunlock`, and `kreboot`.

## Dependencies

Consumed by CPM serial, FCC Ethernet, IRQ, timers, and board code. Requires offset accuracy against MPC8260 hardware documentation and surrounding macros such as `SBIT`.

## Risks

This is a hardware ABI. Structure packing, reserved padding sizes, and field widths must remain exact. Any compiler/layout drift can redirect hardware accesses to wrong registers.
