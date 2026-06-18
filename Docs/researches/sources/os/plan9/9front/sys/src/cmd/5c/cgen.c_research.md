# File Research: sources/os/plan9/9front/sys/src/cmd/5c/cgen.c

This file is the central ARM code generator for C expressions, boolean/control expressions, 64-bit operations, and structure copies.

Main expression generation:
- `cgen()` delegates to `cgenrel()`.
- `cgenrel()` handles assignments, bitfields, integer and floating arithmetic, division/modulo, compound assignment, address generation, function calls, indirection, comparisons, logical operators, casts, struct field access, conditional expressions, and pre/post increment/decrement.
- Uses `addable` and `complex` from `sgen.c:xcom()` to choose between direct moves, address-generation registers, temporary registers, and saved temporaries for function-call-heavy expressions.
- Performs ARM-specific shortcuts:
  - direct immediate arithmetic for constant right operands,
  - signed division/mod by power-of-two constants,
  - multiply-by-constant via `mulcon()`,
  - displacement folding for `OIND`/`OINDREG` when offset fits ARM addressing range.

Compound and bitfield behavior:
- `genasop()` centralizes non-bitfield compound assignments by loading LHS, applying RHS, storing back, and optionally returning the value.
- Bitfield paths use `bitload()` and `bitstore()` from `swt.c`.

Address and boolean generation:
- `reglcgen()` and `lcgen()` compute lvalue addresses, including conditional and comma lvalues.
- `bcgen()` and `boolgen()` emit branch-oriented or value-producing boolean code, including short-circuiting, comparison inversion, floating comparison handling, and constant booleans.

64-bit support:
- `cgen64()` uses register pairs for `vlong`/`uvlong`.
- Handles casts between 32-bit and 64-bit values, assignment operators, shifts, add/sub/and/xor/or, signed/unsigned long multiply into pairs, and multiply-accumulate optimization when adding a 32x32 product to an existing 64-bit pair.
- Uses `freepair()`/`unfreepair()` to temporarily release pair registers while evaluating complex subexpressions.

Structure and block generation:
- `sugen()` handles structure/union and `vlong` movement.
- Supports constants, field extraction, struct literals, structure assignment, function returns by hidden destination pointer, conditional/comma structure expressions, 64-bit direct pair copies, and general block copy.
- General block copy uses `MOVM` register masks in chunks and may emit a loop for larger copies.

Dependencies and interactions:
- Calls register helpers and instruction emitters from `txt.c`.
- Uses `machcap()` to decide when 64-bit lowering is supported.
- Uses `mulcon()` from `swt.c`/`mul.c`, bitfield helpers from `swt.c`, and type/AST helpers from the common C compiler front end.

Research relevance:
- This is the main lowering layer from C AST to ARM `Prog` instructions. It is the highest-risk backend file in this group.

Risk notes:
- Register-pair lifetime handling is subtle; errors in `freepair()`/`unfreepair()` or complex-expression ordering can corrupt 64-bit values.
- Several optimizations mutate AST nodes temporarily, such as zeroing constants to fold addressing offsets.
- Structure copy generation depends on available temp registers and correct `MOVM` masks.
- Floating comparisons deliberately adjust branch conditions for NaN semantics.
