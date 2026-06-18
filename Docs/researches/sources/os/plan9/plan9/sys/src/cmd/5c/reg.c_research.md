# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/reg.c

## Scope

Global register optimizer and data-flow engine for `5c`.

## Behavior

- Builds a control-flow graph of `Reg` nodes from emitted `Prog` instructions.
- Tracks variables as bitsets with `mkvar()`, including globals, parameters, constants, address-taken objects, and physical register use.
- Resolves branch targets, computes reverse postorder/dominators, detects loop structure, and propagates liveness backward.
- Propagates register/variable synchrony forward, computes candidate live regions, ranks them by cost, picks physical registers, and rewrites code with loads/stores.
- Runs the peephole optimizer and then recalculates program counters and branch offsets.

## Dependencies

Uses `gc.h`, compiler `Bits`, `Var`, `Rgn`, `Reg`, `Prog`, type tables, global register arrays, and `peep()` from `peep.c`.

## Risks And Invariants

- Fixed-size region and variable tables (`NVAR`, `NRGN`, `BITS`) bound optimization; overflow degrades or warns rather than resizing.
- `BtoR()` masks out R9/R10 because of Plan 9 ARM conventions for `m` and `g`.
- The algorithm assumes the internal `Prog` list and `Reg` graph remain consistent while inserting moves and excising NOPs.
- Recursion through flow edges can be deep for large functions, matching old compiler assumptions.
