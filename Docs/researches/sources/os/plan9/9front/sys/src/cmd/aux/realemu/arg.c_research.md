# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/arg.c

`arg.c` implements operand objects for the real-mode x86 emulator. It allocates short-lived `Iarg` values from a circular buffer inside `Cpu`, representing registers, memory operands, far pointers, and constants.

`ar` reads an operand with width masking, routing memory through the segment:offset bus mapping and registers through `cpu->reg`. `ars` returns sign-extended values for 1/2/4-byte operands. `aw` writes memory through bus callbacks and preserves unaffected bits for 8- and 16-bit register writes, including high-byte register tags.

This file is the central abstraction between decoded instructions and the bus/register model.
