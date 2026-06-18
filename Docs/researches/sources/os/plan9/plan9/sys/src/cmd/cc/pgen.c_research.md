# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pgen.c

This file generates high-level control-flow code from typed ASTs into architecture back-end operations.

Key behavior:
- `codgen()` emits function prologue pseudo-ops, handles complex returns and register arguments, generates the function body, checks missing returns, and invokes register optimization.
- `gen()` walks statement ASTs and emits branches/code for lists, returns, labels, gotos, cases, switches, loops, `if`, `break`, `continue`, and used/set markers.
- `bcomplex()` type-checks and emits boolean branches for conditions.
- `supgen()` emits code in suppressed-warning mode for unreachable/constant branches.
- `usedset()` emits no-op references to mark volatile/addressed names as used or set.

Important details:
- Reachability state (`canreach`, `warnreach`) drives unreachable-code diagnostics.
- Switch generation delegates case table emission to `doswit()`.
- Loop generation carefully tracks `breakpc`, `continpc`, `nbreak`, and `ncontin`.
- Complex return values are copied through a synthetic `.ret` indirect node.

Filesystem relevance:
- Indirect compiler code generation.
