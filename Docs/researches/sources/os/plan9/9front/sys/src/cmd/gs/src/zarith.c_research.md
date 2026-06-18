# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zarith.c

This file implements Ghostscript/PostScript arithmetic operators for integers and reals.

Key behavior:
- Defines `add`, `sub`, `mul`, `div`, `idiv`, `mod`, `neg`, `abs`, `ceiling`, `floor`, `round`, and `truncate`.
- Exposes `zop_add` and `zop_sub` as reusable helper procedures for direct interpreter and FunctionType 4 use.
- Detects integer overflow in `add`, `sub`, and `mul`, converting overflowing integer results to reals where PostScript semantics allow it.
- Checks divide-by-zero for `div`, `idiv`, and `mod`; handles `MIN_INTVAL / -1` as a rangecheck boundary case for `idiv`.
- Includes a non-standard `.bitadd` integer-only addition operator that deliberately skips the normal overflow conversion semantics.

Important dependencies:
- Uses `oper.h` stack/operator helpers, `store.h` ref construction, and `math_.h` for `ceil`/`floor`.
- Registered through `zarith_op_defs`.

Research notes:
- This is interpreter arithmetic plumbing, not filesystem code, but it is part of the vendored 9front Ghostscript command tree.
- The file explicitly notes that arithmetic operators do not check floating-point exceptions.
