# File Research: sources/os/plan9/9front/sys/src/cmd/qc/reg.c

Global register allocator and data-flow optimizer for the Power C backend.

Key responsibilities:
- `regopt` builds a `Reg` flow graph from `Prog` instructions, records variable uses/sets, resolves branch targets, computes loops, propagates liveness, finds allocation regions, assigns registers, runs peephole optimization, recalculates PCs, fixes branches, and removes NOPs.
- `mkvar` maps memory operands/constants/symbols into bitset-tracked variables.
- `prop` propagates references and call-clobber information backward.
- `loopit`, `postorder`, `rpolca`, `doms`, `loophead`, and `loopmark` estimate loop structure using reverse postorder/dominators.
- `synch`, `paint1`, `paint2`, and `paint3` compute profitable register regions and rewrite memory references to registers.
- `addmove` inserts loads/stores around allocated regions.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map physical registers to allocation bit masks.

Dependencies and coupling:
- Calls `peep()` after allocation.
- Depends on `Bits` operations from the common compiler and target-specific register ranges from `q.out.h`.

Notable behavior:
- Treats calls as clobbering externs and relevant register state.
- Warns and excises stores proven unused.
