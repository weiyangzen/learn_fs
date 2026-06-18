# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/list.c

## Purpose
Provides formatting functions for compiler backend diagnostics, assembly listings, and debug output.

## Key Functions
- `listinit()` installs custom formatters:
  - `%A` opcode,
  - `%B` bitset,
  - `%P` instruction,
  - `%S` string constant,
  - `%D` operand,
  - `%R` register.
- `Bconv()` prints variable bitsets using symbol names or constant offsets.
- `Pconv()` prints `Prog` instructions, with special formats for `ADATA` and `ATEXT`.
- `Aconv()` prints opcode names from `anames[]`.
- `Dconv()` formats abstract operands, including branches, extern/static/auto/param symbols, constants, addresses, indirection, and indexed addressing.
- `Rconv()` prints register names.
- `Sconv()` escapes fixed-size string constants.

## Important Behavior
- Uses Plan 9 assembly syntax in output, e.g. `name+off(SB)`, `name+off(SP)`, `$const`, and `offset(REG)`.
- `Dconv()` temporarily rewrites `D_ADDR` to print address constants recursively.

## Research Notes
This file is support code for making generated abstract instructions inspectable.
