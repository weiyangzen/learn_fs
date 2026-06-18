# File Research: sources/os/plan9/9front/sys/src/cmd/kl/l.h

Primary header for the SPARC linker. It defines linker-side `Adr`, `Prog`, `Sym`, `Auto`, and `Optab` structures; mark flags for scheduling/control-flow analysis; symbol classes; operand classes; buffer globals; layout configuration; linker global state; opcode range tables; and prototypes for all linker passes.

It includes `../kc/k.out.h`, so linker instruction/address enums match compiler and assembler output. The declarations cover object loading, library loading, symbol resolution, data layout, branch patching, no-op/prologue rewriting, scheduling, span computation, assembly output, symbol/line table emission, and diagnostics. This is the shared contract for the `kl` modules.
