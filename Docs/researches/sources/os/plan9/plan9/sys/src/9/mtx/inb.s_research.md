# File Research: sources/os/plan9/plan9/sys/src/9/mtx/inb.s

## Role

PowerPC assembly I/O port access routines for MTX. It implements byte/word/long input/output and repeated string I/O operations.

This is low-level bus I/O support, not filesystem code.

## Main Interfaces

- Input:
  - `inb`
  - `insb`
  - `ins`
  - `inss`
  - `inl`
  - `insl`
- Output:
  - `outb`
  - `outsb`
  - `outs`
  - `outss`
  - `outl`
  - `outsl`

## Important Behavior

- Uses PowerPC load/store byte/halfword/word instructions against I/O-mapped addresses.
- Repeated string operations loop with count registers and branch-on-count helpers.
- Calls `SYNC`/`EIEIO` around I/O operations for ordering.

## Dependencies And Assumptions

- Includes `mem.h`.
- Assumes port numbers are mapped into an addressable I/O region appropriate for `lbz`/`stb` style access.

## Notable Risks

- Endianness and ordering semantics are hardware-specific.
- Count and pointer arguments must match Plan 9 PowerPC calling conventions.
