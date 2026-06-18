# File Research: sources/os/plan9/9front/sys/src/cmd/vi/float.c

`float.c` implements MIPS COP1 floating-point instruction simulation. It dispatches arithmetic, moves, conversions, compares, FP loads/stores, FP condition branches, and register transfers through the `cop1` table.

The code tracks each FP register’s current format (`FPs`, `FPd`, or memory), swaps word order when converting to doubles, updates the FPSR condition bit for compare predicates, handles branch delay slots, and traps unimplemented or invalid operations via `longjmp(errjmp)`.

It supports single, double, and word variants for many operations, but unimplemented COP1 opcodes intentionally stop the simulator.
