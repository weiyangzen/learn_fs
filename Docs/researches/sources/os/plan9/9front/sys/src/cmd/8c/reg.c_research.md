# File Research: sources/os/plan9/9front/sys/src/cmd/8c/reg.c

This file is the 386 backend register optimizer and liveness/dataflow engine.

Key responsibilities:
- Builds a `Reg` control-flow graph from generated `Prog` instructions, excluding data/name/signature pseudo-ops.
- Tracks variable uses, sets, calls, references, register usage, and branch edges.
- Converts branch pc offsets to CFG edges and builds predecessor/successor links.
- Computes loop structure using reverse postorder and approximate dominators.
- Propagates liveness backward with `prop()` and register/variable synchrony forward with `synch()`.
- Finds profitable variable live ranges in `paint1()`, computes unavailable registers in `paint2()`, and rewrites instructions in `paint3()`.
- Inserts load/store moves around allocated regions using `addmove()`.
- Removes unused sets and runs peephole optimization.
- Recomputes pc values and branch offsets after optimization, then removes nops.

Integration points:
- Called by the compiler after initial code generation.
- Uses `mkvar()` to map `Adr` operands to tracked variables.
- Uses peephole helpers from `peep.c` and bitset helpers from common compiler code.

Risks and invariants:
- Only a bounded number of variables (`NVAR`) can be optimized.
- Punned or address-taken variables are marked in `addrs` and avoided.
- Correctness depends on accurate `copyu()` classification for implicit-register x86 instructions.
