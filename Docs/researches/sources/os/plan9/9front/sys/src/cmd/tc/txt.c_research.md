# File Research: sources/os/plan9/9front/sys/src/cmd/tc/txt.c

Provides backend initialization, register allocation helpers, address lowering, instruction emission, type moves, branches, pseudo-ops, and target type tables.

Key points:
- `ginit` initializes the Thumb/ARM backend identity, formatter hooks, program list state, return/safe pseudo nodes, 64-bit support, and register usage.
- `gclean` checks leaked registers, flushes string data, emits global declarations, appends `AEND`, and calls `outcode`.
- `nextpc` allocates and appends a zeroed `Prog`.
- `gargs` and `garg1` evaluate call arguments, precomputing call-heavy arguments into temporaries and assigning register/stack/aggregate argument slots.
- `nodconst`, `nod32const`, `nodfconst`, `nodreg`, `regret`, `regalloc`, `regialloc`, `regfree`, `regsalloc`, `regaalloc1`, `regaalloc`, and `regind` manage temporary nodes and fixed register allocation.
- `naddr` converts AST nodes into backend `Adr` operands; `raddr` extracts register operands.
- `gmove` handles loads, stores, and all scalar/float/integer conversion move opcodes.
- `gins`, `gopcode`, `gopcode2`, `gbranch`, `patch`, and `gpseudo` emit real and pseudo instructions.
- `sconst`, `sval`, and `exreg` classify constants and allocate external register slots.
- `ewidth` and `ncast` define target type widths and legal no-op cast families.

Dependencies and interactions:
- Heavily used by `cgen.c`, `sgen.c`, `swt.c`, and `reg.c`.
- Emits opcodes from `5.out.h` and uses type metadata from the common compiler.

Research relevance:
- This is the backend’s instruction construction and target ABI/layout support layer.
