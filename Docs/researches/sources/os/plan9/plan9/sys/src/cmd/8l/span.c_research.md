# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/span.c

Purpose: instruction sizing, final text address assignment, 386 machine-code encoding, symbols/line tables, and dynamic relocation table emission.

Key behavior: `span` iterates until branch instruction sizes stabilize, aligns data base, defines `etext`, and records function PCs. `asmsym`/`asmlc` emit symbol and line tables. `oclass`, `asmidx`, `asmand`, `doasm`, and `asmins` classify operands and encode ModR/M, SIB, immediates, branches, calls, x87, and special MOV forms. `dynreloc`/`asmdyn` collect and serialize dynamic relocations/imports.

Integration notes: depends on `optab.c` patterns and `pass.c` branch targets. Relocation side effects occur through `vaddr`/`put4` when `dlm` is active. Branch-size convergence is capped at 50 iterations.
