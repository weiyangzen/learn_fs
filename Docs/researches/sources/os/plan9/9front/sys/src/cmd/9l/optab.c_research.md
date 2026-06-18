# File Research: sources/os/plan9/9front/sys/src/cmd/9l/optab.c

This file defines the static operand-pattern table used by the linker to select instruction encodings.

Key content:
- `optab[]` maps assembler opcode plus operand classes to:
  - `type`: encoder case consumed by `asmout`.
  - `size`: emitted byte length.
  - `param`: default base register or helper parameter.
- Covers text pseudo-ops, register moves, arithmetic, logical operations, shifts/rotates, floating-point operations, loads/stores, branches, constants, special registers, compares, traps, cache/TLB operations, raw words, and dynamic relocation forms.

Important interactions:
- `span.c:buildop` sorts this table and expands opcode-range aliases.
- `span.c:oplook` matches instructions against this table.
- `asmout.c:asmout` interprets the selected `type`.

Research notes:
- The table is the declarative bridge between abstract assembler operands and concrete Power64 encoding recipes.
- Several instructions intentionally share patterns through aliasing in `buildop`, rather than duplicating all variants here.
