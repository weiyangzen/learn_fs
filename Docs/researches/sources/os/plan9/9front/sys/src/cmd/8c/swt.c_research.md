# File Research: sources/os/plan9/9front/sys/src/cmd/8c/swt.c

This file groups several backend support tasks: switch lowering, bitfields, string/global data output, object emission, history records, and alignment.

Key responsibilities:
- `swit1()` emits switch dispatch as linear comparisons for small case counts and binary-search comparisons for larger sets.
- `bitload()` and `bitstore()` load, mask, sign/zero extend, and write packed bitfields.
- `outstring()` accumulates string literals into `ADATA` chunks.
- `sextern()` and `gextern()` emit static/global data initializers, including vlong constants split into low/high words.
- `outcode()` writes compiler-generated object instructions to the output file with symbol caching.
- `outhist()`, `zname()`, and `zaddr()` emit source history, symbol-name, and operand records in the Plan 9 object format.
- `align()` and `maxround()` implement 386 ABI layout rules for structs, params, and autos.

Integration points:
- Shares object encoding behavior with `8a/lex.c`.
- Used by front-end global initializer logic and backend code emission.
- Depends on `gc.h`, `8.out.h`, source history globals, and type layout tables.

Risks and invariants:
- `outcode()` appends to an already-open output path and then clears `firstp`/`lastp`.
- Alignment is little-endian-specific for arguments.
- Bitfield operations assume 32-bit container arithmetic.
