# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/reg.c

Purpose: global register allocator and liveness optimizer for the MIPS backend.

Core flow in `regopt`:
- Builds `Reg` nodes for non-data instructions and assigns pseudo-PCs.
- Computes use/set variable bitsets with `mkvar`.
- Resolves branch targets into CFG predecessor/successor links.
- Detects loops with reverse postorder and approximate dominators.
- Propagates references/calls backward (`prop`) and register-variable synchrony forward (`synch`) to fixed point.
- Finds live regions, computes costs with `paint1`, sorts by value, picks registers with `paint2`/`allreg`, and rewrites code with `paint3`.
- Runs `peep`, recomputes PCs, fixes branch offsets, strips NOPs, and recycles `Reg` nodes.

Other functions:
- `addmove` inserts memory/register loads or stores.
- `mkvar` maps operands to optimizable variable slots and classifies externs, params, constants, and address-taken variables.
- `loopit`, `postorder`, `rpolca`, `doms`, `loophead`, and `loopmark` build loop weighting.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map allocatable machine registers to bit masks.

Integration points:
- Driven by common compiler code after code generation.
- Calls `peep.c` and mutates `Prog` streams from `txt.c`.

Risks:
- Optimization is bounded by fixed arrays (`NVAR`, `NRGN`, bitset size).
- Alias handling is conservative through `addrs`, but missed address-taking classification would be unsafe.
- Register bit mapping excludes reserved MIPS registers and only allocates even floating registers.
