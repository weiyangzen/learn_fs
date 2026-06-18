# File Research: sources/os/plan9/9front/sys/src/cmd/ki/run.c

Core SPARC instruction dispatch and integer/control instruction emulator for `ki`. It defines opcode tables for format-0, format-2, and format-3 instruction classes, then `run` repeatedly fetches, dispatches, increments PCs, and checks instruction breakpoints. `delay` executes branch delay slots, and branch handlers implement annul semantics.

The file covers arithmetic/logical ops, condition-code variants, shifts, Y register access, `mulscc`, loads/stores, `ldstub`, `swap`, `sethi`, calls, jumps, and integer/FP branches. It tracks instruction counts, taken branches, delay-slot use, nops, and load interlocks. Unsupported encodings call `undef` and return to the debugger.
