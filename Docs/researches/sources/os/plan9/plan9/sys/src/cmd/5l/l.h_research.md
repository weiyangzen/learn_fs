# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/l.h

## Scope

Central header for `5l`.

## Contents

- Defines linker core structs: `Adr`, `Prog`, `Sym`, `Autom`, `Optab`, `Oprang`, and `Count`.
- Defines symbol types, opcode classification classes, mark flags, buffer sizes, hash limits, hunk size, relocation bit packing, and globals.
- Declares all major linker passes: object loading, patching, data layout, flow ordering, no-op/prologue work, span/literal work, assembly output, imports/exports, diagnostics, and formatting.

## Dependencies

Includes Plan 9 `u.h`, `libc.h`, `bio.h`, ARM object constants from `../5c/5.out.h`, and ELF definitions from `../8l/elf.h`.

## Risks And Invariants

- Uses union field macros heavily; many fields have context-dependent meaning.
- Many global variables are shared across passes, making pass order strict.
- Relocation packing limits are fixed by `Roffset` and `Rindex`.
