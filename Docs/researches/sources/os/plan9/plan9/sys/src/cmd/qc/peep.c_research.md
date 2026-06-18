# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/peep.c

Late peephole optimizer for PowerPC compiler output.

Key responsibilities:
- Completes the `Reg` flow graph by inserting missing nodes for non-data instructions between register-allocation nodes.
- Eliminates redundant register-to-register moves through copy propagation.
- Performs substitution propagation to swap register names and expose removable moves.
- Converts `$0` constants to `REGZERO` when the target treats R0 as a zero register.
- Removes redundant byte/halfword extension move pairs.
- Folds `CMP reg,$0` followed by conditional branches into condition-code-setting forms of the producer instruction when legal.
- Tracks instruction register use/set behavior through `copyu`, `copyau`, `copysub`, and related helpers.

Dependencies:
- Depends on `Reg`, `Prog`, `Adr`, PowerPC opcode enums, zero-register policy, and backend flow graph links from `reg.c`.

Notable risks:
- Copy propagation is conservative around calls, returns, branches, read-alter-write operations, and ambiguous opcodes.
- Many instruction semantics are hand-classified; missing a use/kill case can miscompile.
- Floating-point compare folding is intentionally disabled/commented out.
