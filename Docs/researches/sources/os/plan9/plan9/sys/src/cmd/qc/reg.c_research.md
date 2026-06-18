# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/reg.c

Global register allocator and data-flow optimizer for the PowerPC C compiler backend.

Key responsibilities:
- Builds an auxiliary `Reg` flow graph from generated `Prog` instructions.
- Tracks variables, uses, sets, constants, externs, params, aliases, and register-bit occupancy.
- Resolves branch targets and predecessor/successor links.
- Computes approximate loop structure using reverse postorder and dominator-style analysis.
- Propagates liveness backward and register/variable synchrony forward.
- Identifies profitable live regions, chooses free integer or floating registers, inserts loads/stores, and rewrites operands.
- Runs peephole optimization afterward and recalculates program counters/branch targets.
- Eliminates dead stores and removes `ANOP`s before freeing flow structures.

Dependencies:
- Uses `gc.h` optimizer structures, bitsets, PowerPC register ranges, instruction classifications, and `peep()`.

Notable risks:
- Variable recognition in `mkvar()` deliberately excludes or marks aliased/punned/address-taken values.
- Costing depends on loop weights and constants such as `CLOAD`, `CREF`, and `CINF`.
- Correctness relies on handwritten instruction use/set classification.
