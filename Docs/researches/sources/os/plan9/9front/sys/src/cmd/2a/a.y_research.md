# File Research: sources/os/plan9/9front/sys/src/cmd/2a/a.y

Purpose: Yacc grammar for the 68020 assembler language accepted by `2a`.

Key behavior:
- Parses labels, symbol assignments, instructions, and semicolon-terminated lines.
- Maps lexer token classes `LTYPE1` through `LTYPEB` to instruction operand forms, then calls `outcode()` with a populated `Gen2`.
- Supports no-operand, source-only, destination-only, source/destination, data pseudo-op, bit-field, text, relative branch, and DBcc-style instruction forms.
- Expression grammar supports constants, variables, unary sign/complement, arithmetic, shifts, bitwise operators, and parentheses.
- Addressing grammar covers constants, `$` immediates, string/floating immediates, TOS offsets, register direct modes, predecrement/postincrement address registers, symbol references through `SB`/`SP`/`FP`, statics with `<>`, branches through `PC`, and 68020 indexed addressing forms.
- Indexed forms encode `.W`/`.L` width and `*1/*2/*4/*8` scale into `Gen.index`, `Gen.scale`, and `Gen.displace`.

Research notes:
- Undefined labels are tolerated in pass 1 but diagnosed in pass 2.
- `DATA` and `TEXT` use special productions to carry width/frame metadata in `Gen.displace`.
- Bit-field syntax stores offset/width metadata in `field` fields used later by object writers/linkers.
