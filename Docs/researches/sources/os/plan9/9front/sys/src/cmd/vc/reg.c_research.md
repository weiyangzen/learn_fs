# File Research: sources/os/plan9/9front/sys/src/cmd/vc/reg.c

Purpose: Global register optimizer and dataflow engine for the MIPS backend.

Key behavior:
- Builds a `Reg` node graph over real instructions, excluding metadata pseudo-ops.
- Computes use/set bitsets for tracked variables and builds branch successor/predecessor links.
- Marks loops using reverse postorder and approximate dominators.
- Propagates reference/call liveness backward and register/variable synchrony forward to fixed point.
- Warns on used-not-set and set-not-used variables; excises unused sets.
- Finds profitable live regions with `paint1`, determines conflicting registers with `paint2`, chooses available integer/FP registers, and rewrites code with `paint3`.
- Inserts loads/stores around allocated live regions via `addmove`.
- Recomputes program counters, fixes branch targets, removes nops, and runs peephole optimization.
- Maps allocatable MIPS integer and floating registers to bit masks.

Dependencies:
- Uses backend bitset helpers, `Var` table, `Prog` address classes, `peep`, and target register constants from `v.out.h`.

Notable details:
- Integer register allocation covers R3-R23; FP allocation covers even F4-F22.
- Extern/static/param/address-taken variables are treated conservatively in dataflow.
