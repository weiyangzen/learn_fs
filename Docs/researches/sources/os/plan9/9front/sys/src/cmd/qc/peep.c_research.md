# File Research: sources/os/plan9/9front/sys/src/cmd/qc/peep.c

Peephole optimizer for Power instructions after global register allocation. It works over the `Reg` control-flow graph and mutates `Prog` instructions in place.

Key responsibilities:
- Completes missing `Reg` nodes for instructions between flow graph nodes.
- Repeatedly performs copy propagation and substitution propagation for register moves.
- Converts constant zero moves to `R0` references when the target treats `R0` as zero.
- Removes redundant byte/halfword sign/zero extension pairs.
- Folds `OP x,y,R; CMP R,$0; branch` into condition-code-setting `OPCC` instructions where safe.
- `copyu`, `copyas`, `copyau`, `copysub`, and related helpers classify and rewrite instruction uses/sets.

Dependencies and coupling:
- Called from `reg.c` unless register debug suppresses it.
- Depends on Power opcode semantics and `R0ISZERO`.
- Uses `Reg` graph predecessor/successor helpers `uniqp` and `uniqs`.

Notable behavior:
- Floating condition-code folding is intentionally disabled in comments.
- Unknown instructions are treated conservatively as read-alter-rewrite barriers.
