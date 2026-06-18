# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/optab.c

Purpose: 386 instruction encoding table.

Key behavior: declares operand-pattern tables (`y*`) and `optab[]`, mapping each 8.out opcode to accepted operand classes, prefix mode, and raw opcode bytes/extension fields. Covers integer, branch, stack, segment/control/debug/task register, string, and x87 instructions.

Integration notes: consumed by `span.c` `doasm`. Table order must match opcode enum values checked in `obj.c`; incorrect patterns alter instruction size and can destabilize branch span convergence.
