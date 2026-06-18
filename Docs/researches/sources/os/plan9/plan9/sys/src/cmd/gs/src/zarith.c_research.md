# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarith.c

Implements Ghostscript PostScript arithmetic operators: `abs`, `add`, `.bitadd`, `ceiling`, `div`, `idiv`, `floor`, `mod`, `mul`, `neg`, `round`, `sub`, and `truncate`.

Key behavior:
- `zop_add` and `zop_sub` are exported helper paths used directly by the interpreter and FunctionType 4 code.
- Integer operations preserve integer results when possible, converting to real on detected overflow for `add`, `sub`, `mul`, and `neg(MIN_INTVAL)`.
- `div` always returns real quotient and checks divide-by-zero; `idiv` and `mod` require integer operands and reject zero divisors.
- Rounding operators accept integer or real operands and leave integers unchanged.
- `.bitadd` is a non-standard integer-only addition without overflow conversion.

Dependencies and coupling:
- Uses operand-stack refs from `oper.h` and typed constructors/checks from `store.h`.
- Depends on `math_.h` for `ceil` and `floor`.
- Explicit file note says arithmetic operators do not currently check floating exceptions.
