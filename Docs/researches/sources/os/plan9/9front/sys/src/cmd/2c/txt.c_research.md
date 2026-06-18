# File Research: sources/os/plan9/9front/sys/src/cmd/2c/txt.c

Purpose: target initialization, instruction selection tables, address lowering, register allocation primitives, and low-level instruction emission for `2c`.

Key behavior:
- `ginit()` initializes target identity, register availability, register base mapping, move/cast table `txt`, operation-to-opcode table `opxt`, string/static/rathole symbols, return node, zero program, and 64-bit helpers.
- `gclean()` verifies all registers freed, flushes pending strings, computes special symbol widths, emits `AGLOBL`s, appends `AEND`, and calls `outcode()`.
- `oinit()` populates type-indexed opcode choices for byte/word/long/float/double operations.
- `nextpc()` appends a new `Prog` and increments logical PC.
- `gargs()` evaluates function arguments onto `D_TOS`.
- `naddr()` converts compiler `Node` forms into `Adr` forms, including statics/externs/autos/params, constants, address/indirection, and indexed modes.
- `regalloc()`, `regaddr()`, `regpair()`, `regret()`, and `regfree()` manage temporary data/address/FPU registers.
- `gmove()` emits typed moves and casts, including clear/extend behavior, float/int conversions, unsigned long to float adjustment, and FPCR rounding-mode changes for float-to-int.
- `gopcode()` emits a typed instruction after lowering tree operands and optional indexed operands.
- `asopt()` rewrites simple moves to `CLR`, `PEA`, or quick-constant-through-register sequences.
- `gbranch()`, `fpbranch()`, `patch()`, `gpseudo()`, and `gpseudotree()` create branches and pseudo-ops.
- `exreg()` allocates external register variables within target register limits.

Research notes:
- `ewidth[]` and `ncast[]` at file end define target size and legal no-op cast masks.
- Address registers A6/A7 are reserved early as SB/SP.
