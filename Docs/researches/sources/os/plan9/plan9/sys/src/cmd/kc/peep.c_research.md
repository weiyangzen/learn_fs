# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/peep.c

This file implements peephole and local copy-propagation optimization over the backend `Reg` control-flow list.

`peep()` first completes the `Reg` structure by adding missing nodes for instructions between flow graph nodes, then repeatedly removes redundant register-to-register and zero-register moves when `copyprop()` or `subprop()` proves it safe. It also removes redundant repeated byte/halfword sign/zero-extension moves.

`subprop()` rewrites register usage around a copy to improve copy propagation opportunities. `copyprop()` and `copy1()` recursively propagate substitutions through successor paths while respecting merges and sets.

`copyu()`, `copyas()`, `copyau()`, `copyau1()`, `copysub()`, and `copysub1()` encode per-instruction read/write behavior. Calls, returns, branches, and unknown instructions are treated conservatively.

This pass is tightly coupled to SPARC instruction semantics and the register allocator’s flow graph. Its main risk is semantic misclassification of instruction operands, which would make propagation unsafe.
