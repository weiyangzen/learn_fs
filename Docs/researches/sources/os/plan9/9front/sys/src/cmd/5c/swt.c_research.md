# File Research: sources/os/plan9/9front/sys/src/cmd/5c/swt.c

This file implements switch lowering, bitfield load/store helpers, string/global data emission, multiply-by-constant emission, object writing, history output, and ABI alignment.

Switch lowering:
- `swit1()` allocates a temp and calls `swit2()`.
- `swit2()` chooses:
  - direct jump table via `ACASE`/`ABCASE` when case density is high,
  - linear compare/branch for fewer than five cases,
  - binary search over sorted cases otherwise.
- Direct tables insert default entries for holes and finish with a branch to default to keep `regopt()` stable.

Bitfields:
- `bitload()` loads, shifts, and sign/zero-extends bitfield values.
- `bitstore()` masks, shifts, merges, stores back, and optionally returns the assigned bitfield value.

Data and multiply helpers:
- `outstring()` emits string data in `NSNAME` chunks through `ADATA`.
- `mulcon()` uses `mulcon0()` to emit shift/add/sub sequences for constant multiplication.
- `sextern()` emits static string/global byte data.
- `gextern()` emits global data, including split 64-bit constants respecting target endianness.

Object output:
- `zwrite()` serializes a `Prog`.
- `outcode()` optionally lists instructions, emits history, interns symbols into the object symbol cache, writes every `Prog`, then clears the instruction list.
- `outhist()` writes path and line history records.
- `zname()` writes `ANAME` or `ASIGNAME` symbol records.
- `zaddr()` serializes object operands.

ABI layout:
- `align()` implements ARM struct, element, argument, and automatic-storage alignment.
- `maxround()` rounds and tracks maximum stack/safe-space use.

Dependencies and interactions:
- Uses switch case lists from the front end, `gopcode()`/`gbranch()`/`gpseudo()` from `txt.c`, and multiply plans from `mul.c`.
- Object writer mirrors `5a/lex.c` serialization logic.

Research relevance:
- Combines multiple backend support surfaces: switches, bitfields, constants, final object output, and ABI alignment.

Risk notes:
- Direct switch lowering depends on `ACASE` and linker/runtime interpretation of `ABCASE`.
- `bitstore()` assumes `n2`/`n3` were provided by `bitload()` and frees them.
- `align()` hardcodes little-endian argument adjustment behavior.
