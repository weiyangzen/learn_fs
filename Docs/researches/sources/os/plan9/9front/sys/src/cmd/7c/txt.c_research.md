# File Research: sources/os/plan9/9front/sys/src/cmd/7c/txt.c

Central ARM64 code emission and backend setup file for `7c`. It initializes target state, manages temporary/register allocation, emits instructions, selects move/cast/arithmetic opcodes, handles branches/pseudo-ops, validates immediates/offsets, and defines target type tables.

Key areas:
- `ginit` sets target identity, register reservations, type-class tables, zero/template nodes, return/temp nodes, and compiler globals.
- `gclean` checks leaked registers, flushes string literals, emits `AGLOBL` records, appends `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gopcode`, `gbranch`, `patch`, and `gpseudo` allocate and populate `Prog` instructions.
- `gargs`/`garg1` lower call arguments, including function-call temporaries, structure pass-by-pointer handling, first argument register use, and stack argument layout.
- `regalloc`, `regfree`, `regret`, `regsalloc`, `regaalloc`, and related helpers manage backend scratch registers and stack temporaries.
- `naddr`/`raddr` convert compiler `Node` objects into assembler `Adr` operands.
- `gmove` is the large type-conversion/move selector covering integer, pointer, vlong, float, double, load/store, sign-extension, zero-extension, and float/int conversions.
- `gopcode` maps generic C operators to ARM64 opcodes and emits comparison-plus-branch sequences, including zero-compare optimizations through `zcmp`.
- `usableoffset`, `sval`, and `isaddcon` gate ARM64 immediate/addressing encodings.

Data tables:
- `ewidth` defines target type widths.
- `ncast` defines no-op cast compatibility classes.

Important constraints:
- `REGTMP`, SB, link, SP/zero, and two external registers are reserved.
- `REGARG` is `R0`, so call and return paths share register pressure decisions.
- `gmove` avoids redundant same-register moves with `samaddr`.

Filesystem relevance: indirect compiler backend.
