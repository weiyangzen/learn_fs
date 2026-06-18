# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/defs.h

## Purpose
Supplies user-space glue definitions borrowed from kernel UBIFS expectations: endian conversions, branch prediction/assertion stubs, `struct qstr`, `fls()`, and `do_div()`.

## Main Definitions
- `t16()`, `t32()`, and `t64()` conditionally byte-swap based on host endianness.
- `cpu_to_le*()` and `le*_to_cpu()` wrap little-endian conversions for UBIFS on-media structures.
- `unlikely()` and `ubifs_assert()` are no-op user-space stand-ins.
- `struct qstr` stores a name pointer and length.
- `fls()` returns the position of the most significant set bit in a 32-bit int.
- `do_div()` divides an integer-like lvalue and returns the remainder.

## Dependencies
Assumes includers provide byte-swap macros, endian macros, integer types, and `INT_MAX`.

## Risks and Notes
`do_div()` casts through `unsigned long`, so it is only a faithful 64-bit helper on platforms where `unsigned long` is wide enough for the values used by mkfs.ubifs. The file enforces 32-bit `int` and 64-bit `long long` at compile time.
