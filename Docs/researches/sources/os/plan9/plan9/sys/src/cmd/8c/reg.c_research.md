# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/reg.c

## Purpose
Global register optimizer for the Plan 9 386 compiler backend.

## Key Phases in `regopt()`
- Builds `Reg` control-flow nodes for non-data instructions.
- Computes use/set bits for variables and implicit register use.
- Resolves branch targets into CFG edges.
- Computes loop weighting with reverse postorder and approximate dominators.
- Propagates liveness backward with `prop()`.
- Propagates register/variable synchrony forward with `synch()`.
- Identifies profitable live regions with `paint1()`.
- Determines available registers with `paint2()` and `allreg()`.
- Rewrites instructions and inserts loads/stores with `paint3()`.
- Runs `peep()` and recalculates PCs/branch offsets.
- Removes `ANOP`s and recycles analysis nodes.

## Key Helpers
- `mkvar()` maps memory operands to optimizable variable bits.
- `addmove()` inserts variable-register load/store moves.
- `doregbits()`, `RtoB()`, `BtoR()` convert between register numbers and bit masks.
- `loopit()`, `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()` estimate loop structure.
- `regset()` and `reguse()` query register effects through `copyu()`.

## Important Behavior
- Avoids optimizing externs, params, address-taken variables, constants, and unsafe punning cases.
- Reserves stack pointer and accumulator defaults through `regbits`.
- Accounts for implicit register clobbers from division, string ops, calls, returns, floating status, and shift/string instructions.
- Uses loop depth to weight optimization profitability.

## Research Notes
This is the backend’s global data-flow pass. It rewrites abstract assembly before final object emission.
