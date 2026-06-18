# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/txt.c

Purpose: low-level MIPS instruction emission, register allocation helpers, moves/conversions, branching, pseudo-ops, and type width/cast tables.

Core initialization:
- `ginit` sets target identity (`thechar = 'v'`, `thestring = "mips"`), initializes globals, special nodes, rathole/return nodes, 64-bit support, and reserved registers.
- `gclean` validates register state, flushes pending string data, emits globals, emits `AEND`, and calls `outcode`.

Register/address helpers:
- `nextpc` allocates `Prog` records.
- `gargs`/`garg1` handle call argument evaluation, including function-call temporaries and first-argument register passing.
- `regalloc`, `regfree`, `regialloc`, `regsalloc`, `regaalloc1`, and `regaalloc` manage temporary registers and stack argument locations.
- `naddr` lowers compiler `Node` operands to backend `Adr` operands.

Instruction emission:
- `gmove` implements loads, stores, scalar conversions, float/integer conversions, constants, and special floating constants.
- `gins` emits a raw instruction.
- `gopcode` maps compiler operations to MIPS opcodes, including multiply/divide LO/HI handling and compare/branch generation.
- `gbranch`, `patch`, and `gpseudo` emit branches and pseudo-ops.
- `sconst`, `sval`, and `exreg` support immediate/register-variable decisions.
- `ewidth` and `ncast` define target type widths and no-cast compatibility masks.

Risks:
- Float-to-int conversion manipulates FCR31 and emits NOPs; this is highly target-specific and fragile.
- Register allocation uses global `reg[]` counts and must be balanced exactly.
- `regfree` checks `i >= sizeof(reg)`, which compares an index to bytes, not element count; the oversized bound is unlikely to fail safely for bad indices.
