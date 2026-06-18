# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/gc.h

Central ARM `5c` backend header.

Key contents:
- ARM data-size constants and backend flags.
- `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn` structures.
- Global compiler backend state for generated instruction lists, registers, regions, variables, cases, constants, and optimization data.
- Register allocator and optimizer bitset macros.
- Prototypes for code generation, text emission, switch lowering, bitfield handling, listing, register optimization, peephole optimization, predicate optimization, and multiply optimization.

Notes:
- Defines `BTRUE` relation flag and ARM-specific register allocation ranges.
- `NRGN` is raised for large source files.
