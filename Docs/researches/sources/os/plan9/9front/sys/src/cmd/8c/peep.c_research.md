# File Research: sources/os/plan9/9front/sys/src/cmd/8c/peep.c

This file implements peephole and copy-propagation optimizations over the backend control-flow graph.

Key responsibilities:
- Fills missing `Reg` nodes for non-control pseudo-free instruction gaps.
- Iteratively removes redundant register-to-register `MOVL` instructions via `copyprop()` and `subprop()`.
- Simplifies sign/zero-extension chains when consecutive moves make the second extension redundant.
- Rewrites `LEAL` followed by matching load into a direct `MOVL` where safe.
- Converts add/sub by ±1 to inc/dec when condition-code users do not require carry.
- Removes compare-with-zero instructions when previous arithmetic already produced usable flags.
- Provides dataflow helpers:
  - `uniqp()`/`uniqs()` for unique predecessor/successor.
  - `copyu()` for use/set classification.
  - `copyas()`, `copyau()`, and `copysub()` for operand substitution.

Integration points:
- Invoked by `regopt()` after register allocation.
- Uses `copyu()` semantics also needed by register allocation to determine register use/set behavior.
- Emits removal by converting instructions to `ANOP`.

Risks and invariants:
- x86 implicit-register instructions are conservatively treated as blockers.
- Flag-sensitive transformations rely on `needc()` to avoid breaking carry-dependent code.
- Unknown opcodes default to unsafe read-alter-write behavior.
