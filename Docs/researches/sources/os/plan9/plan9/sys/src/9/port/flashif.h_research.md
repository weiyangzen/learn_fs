# File Research: sources/os/plan9/plan9/sys/src/9/port/flashif.h

Purpose: Shared flash/NAND interface definitions for Plan 9 flash drivers and `devflash`-style code.

Contents:
- Defines logical `Flashpart`, physical `Flashregion`, per-chip `Flashchip`, and runtime `Flash`.
- `Flash` includes card type, mapped address, size, XIP flag, reset hook, erase/read/write/suspend/resume/attach hooks, width/interleave/command parameters, partition table, protection state, and flash sort.
- Declares flash card registration, architecture flash reset/write-protect, width-aware flash accessors, and NAND-specific architecture hooks.

Dependencies and integration:
- Used by architecture flash probes, CFI/NAND/NOR/serial drivers, and flash device code.

Risks and notes:
- Header defines the contract only; hardware drivers fill function pointers and geometry.
- NAND hooks abstract claim/power, CLE/ALE, byte reads, and byte writes.
