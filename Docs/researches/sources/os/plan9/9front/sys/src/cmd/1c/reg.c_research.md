# File Research: sources/os/plan9/9front/sys/src/cmd/1c/reg.c

Global register optimizer and flow/liveness engine for `1c`.

Key responsibilities:
- Builds a `Reg` flow graph from the generated `Prog` list, recording use/set sets for variables and registers.
- Resolves branch targets and builds predecessor/successor links.
- Computes loop structure using reverse postorder and approximate dominators.
- Propagates reference/call liveness backward and register/variable synchrony forward to fixed point.
- Warns on used-before-set and set-not-used variables, excising dead stores.
- Identifies profitable live regions, assigns data/address/FP registers, and rewrites memory references to registers.
- Inserts load/store moves at region boundaries and preserves CCR around inserted moves when needed.
- Runs peephole optimization after register allocation and recalculates final PCs/branches.

Important dependencies:
- Uses `mkvar` to classify optimizable extern/static/auto/param variables.
- Uses target register bit masks for D, A, and F registers.

Notable details:
- The optimizer accounts for 68040 denormal FP load behavior by forcing initialization moves for some auto FP variables.
- Address registers are chosen when cheaper than data registers for eligible integer/pointer variables.
