# File Research: sources/os/plan9/9front/sys/src/cmd/kl/optab.c

This file defines `optab[]`, the SPARC instruction selection/encoding table used by `oplook()` and later assembly emission. Each row maps an opcode plus operand classes to an encoding case number, instruction size, and optional implicit register.

The table covers text/nop records, integer moves, constants, memory forms, ASI accesses, processor registers, arithmetic/comparison forms, jumps/branches/traps, floating-point moves/compares/ops, raw words, division/modulo helper forms, and aliases that are expanded in `buildop()`.

It has no executable logic beyond the table. Its correctness depends on class definitions and assembler emission cases in the rest of the `kl` backend matching these numeric encoding cases and sizes exactly.
