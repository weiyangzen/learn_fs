# File Research: sources/os/plan9/9front/sys/src/cmd/6c/sgen.c

- Role: Expression complexity/addressability analysis and selected codegen setup helpers for 6c.
- `noretval()` emits dummy NOP references to integer and/or floating return registers to mark return-value liveness.
- `xcom()` recursively annotates expression trees with `addable` and `complex` scores used by code generation and register scheduling.
- Addressability model recognizes constants, names, registers, indirections, address-of forms, folded pointer-plus-constant expressions, and amd64 indexed addressing forms.
- Converts multiply/divide/modulo by powers of two into shifts/masks when valid, and commutes expressions to put more complex operands first.
- Builds OINDEX address expressions through `indx()` and global `idx` state, including base/index/scale extraction.
- `indexshift()` marks small left shifts as scaled-index candidates.
- Complexity penalties are added for calls, casts involving unsigned vlong to floating types, multiply/divide/modulo, and shifts/rotates.
- Comparison normalization moves constants to the left and inverts relation operators to match backend compare expectations.
