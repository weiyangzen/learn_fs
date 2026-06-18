# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/asm.c

## Scope

Final assembler/output writer for the Plan 9 ARM linker (`5l`).

## Behavior

- `asmb()` writes text, literal/string text data, data segment, symbols, line tables, dynamic module records, and executable headers for multiple head types.
- Provides buffered byte/word/long writers in big- and little-endian variants.
- Emits Plan 9 symbols and line number tables.
- `datblk()` materializes initialized data/string blocks with endian conversion, floating constants, symbol relocation, and duplicate-initialization checks.
- `asmout()` maps linker `Optab` encoding types to concrete ARM, old FPA, and VFP machine words.
- Helper encoders build ALU, branch, load/store, halfword, VFP memory, literal-load, and floating immediate encodings.

## Dependencies

Uses linker globals from `l.h`, opcode tables from `optab.c`, addressing classification from span logic, dynamic relocation helpers, and ELF writer support.

## Risks And Invariants

- `asmout()` relies on `Optab.type` numbers staying synchronized with `optab.c`.
- Relocation and literal handling uses `p->cond` both for branch targets and literal pool entries.
- Output buffering does not check write return values.
- ARM immediate and offset span diagnostics are late, during final encoding.
