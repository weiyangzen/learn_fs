# File Research: sources/os/plan9/9front/sys/src/cmd/7c/reg.c

Global register optimizer for the ARM64 compiler backend. It builds a control-flow graph over emitted `Prog` instructions, performs liveness and synchronization propagation, identifies profitable variable live ranges, assigns hardware registers, rewrites instructions, runs peephole optimization, and repairs PCs/branches.

Key phases in `regopt`:
- Builds `Reg` nodes while skipping data/name pseudo-ops.
- Computes variable use/set bitsets through `mkvar`.
- Resolves branch targets into CFG successor/predecessor links using `log5` skip links for faster lookup.
- Computes loop weights using reverse postorder, approximate dominators, and loop-head marking.
- Propagates references and call-live sets backward through `prop`.
- Propagates register/variable divergence forward through `synch`.
- Finds candidate allocation regions using `paint1`, scores them, sorts by cost with `rcmp`, computes occupied register masks with `paint2`, chooses registers with `allreg`, and rewrites with `paint3`.
- Runs `peep` unless disabled by debug settings.
- Recalculates PCs, fixes branch offsets, removes NOPs, and recycles `Reg` nodes.

Important helpers:
- `addmove` inserts spill/reload moves around regions.
- `mkvar` tracks symbolic variables and classifies externs, params, constants, and address-taken/punned variables.
- `addreg` rewrites an address to a chosen register.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map ARM64 register numbers to allocator bit masks.

Constraints:
- Register candidates are limited to backend-defined allocatable ranges.
- Variables with funny punning, excessive variable count, or unsafe address identity are excluded from optimization.

Filesystem relevance: indirect compiler optimizer.
