# File Research: sources/os/plan9/9front/sys/src/cmd/tc/reg.c

Implements global register allocation and data-flow optimization for the Thumb compiler backend.

Key points:
- `regopt` builds a `Reg` control-flow graph from emitted `Prog`s, records variable uses/sets, links branches, computes loop structure, propagates liveness and synchrony, identifies profitable live regions, assigns registers, rewrites code, runs peephole optimization, recomputes program counters, patches branches, removes `NOP`s, and recycles `Reg` nodes.
- `mkvar` maps address operands to tracked variables and classifies externs, params, constants, and address-taken/punned variables.
- `prop` propagates reference/call liveness backwards through predecessors.
- `postorder`, `rpolca`, `doms`, `loophead`, `loopmark`, and `loopit` compute reverse postorder, approximate dominators, and loop weighting.
- `synch` propagates variable/register synchrony forward.
- `paint1` scores a candidate live region; `paint2` finds register conflicts; `allreg` selects integer or float registers; `paint3` rewrites references to use the chosen register and inserts loads/stores with `addmove`.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map registers to allocator bit masks.

Dependencies and interactions:
- Calls `peep` unless disabled by debug flags.
- Uses instruction emission/address structures from `gc.h` and formatting helpers for diagnostics.
- Inserts actual load/store instructions by allocating new `Prog` nodes.

Research relevance:
- This is the main backend optimizer and register allocator for generated Thumb code.
