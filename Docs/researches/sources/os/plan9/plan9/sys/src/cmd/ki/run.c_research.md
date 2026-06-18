# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/run.c

This is the core SPARC instruction emulator for `ki`.

It defines opcode dispatch tables for op0/op2/op3 instruction classes and `run()` fetches, decodes, counts, dispatches, advances PC, and checks instruction breakpoints. `delay()` executes delay-slot instructions while preserving the branch target behavior, and tracks used delay slots.

Implemented instruction families include integer arithmetic/logical ops, condition-code variants, shifts, carry add/sub behavior, Y register access, `mulscc`, loads/stores, double loads/stores, byte/halfword sign/zero loads, `ldstub`, `swap`, `sethi`, `call`, `jmpl`, integer branches, trap/syscall dispatch, and floating hooks via `float.c`.

Condition-code logic updates PSR `N/Z/V/C` for relevant arithmetic. Branches compute signed displacement targets, implement annul behavior, track taken counts, and execute delay slots correctly. `ilock()` models load-use stalls for profiling.

The file is large and semantics-heavy; correctness depends on matching SPARC v8 behavior and Plan 9 calling/syscall conventions.
