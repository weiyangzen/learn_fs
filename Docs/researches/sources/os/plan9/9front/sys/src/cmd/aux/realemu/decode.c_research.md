# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/decode.c

`decode.c` maps x86 opcodes to `Inst` structures. It contains primary and `0F` opcode tables plus selected group tables for arithmetic, shifts, tests, pushes/pops, calls/jumps, string ops, segment overrides, operand/address-size prefixes, conditional moves/jumps/sets, bit operations, and basic CPUID.

The decoder handles instruction prefixes, ModR/M and SIB decoding for 16-bit and 32-bit addressing, default segment selection, displacements, immediates, far pointers, string source/destination operands, segment registers, and high-byte registers.

Unsupported or arcane instructions are represented as `OBAD`, causing execution to trap later. Group decoding switches on the ModR/M `reg` field after operands are initially resolved.

This file is decode-only; actual semantics are in `xec.c`.
