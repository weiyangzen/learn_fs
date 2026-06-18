# File Research: sources/os/plan9/9front/sys/src/cmd/5c/reg.c

This file implements global register allocation and data-flow optimization for the ARM C backend.

Main flow in `regopt()`:
- Builds a `Reg` node graph for real instructions, skipping data/global/name pseudo records.
- Assigns synthetic PCs and `log5` skip links for branch target lookup.
- Computes per-instruction use/set bitsets with `mkvar()`.
- Converts branch target offsets to `Reg` successor pointers and back-pointers.
- Detects loop structure with reverse postorder and approximate dominators via `loopit()`.
- Propagates liveness backward with `prop()`.
- Propagates register/variable synchrony forward with `synch()`.
- Warns and removes dead sets.
- Identifies allocation regions with `paint1()`, scores them, sorts by cost, selects registers with `allreg()`/`paint2()`, and rewrites instructions with `paint3()`.
- Runs `peep()` unless disabled by debug flags.
- Recomputes PCs, fixes branches, removes `ANOP`s, and recycles `Reg` nodes.

Supporting routines:
- `rega()` allocates/reuses `Reg` nodes.
- `rcmp()` sorts regions by cost.
- `addmove()` inserts load/store moves around a region for assigned variables.
- `mkvar()` maps object addresses to variable bitsets and classifies externs, params, constants, and address-taken/punned variables.
- `prop()` performs backward reference/call propagation across branches and calls.
- `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()`, and `loopit()` implement loop weighting.
- `synch()` propagates differences between memory and register state.
- `allreg()` chooses an integer or floating register based on type and availability.
- `paint1()`, `paint2()`, and `paint3()` score, collect conflicts, and rewrite a variable’s live region.
- `addreg()` rewrites an `Adr` to a selected register.
- `RtoB()`, `BtoR()`, `FtoB()`, and `BtoF()` map physical registers to bit masks.

Register policy:
- Integer allocation candidates are roughly `R2`-`R8`; `BtoR()` excludes `R9` and `R10` for `m` and `g`.
- Floating allocation candidates are `F2`-`F7`.

Dependencies and interactions:
- Uses `Bits` operations from the common compiler, ARM register constants, `var[]`, and peephole routines.
- Consumes `Prog` chains emitted by `txt.c`/`cgen.c`.

Research relevance:
- This is the global optimizer for generated ARM code.

Risk notes:
- Variable identity in `mkvar()` is based on symbol/name/offset and etype; aliasing and punning are conservatively marked through `addrs`.
- The register allocator modifies instruction operands in place and inserts loads/stores; wrong liveness propagation can produce stale memory or overwritten registers.
- Calls and returns have special liveness semantics for externs, return regs, and argument regs.
