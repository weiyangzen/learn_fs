# File Research: sources/os/plan9/9front/sys/src/cmd/ql/pass.c

This file implements major non-emission linker passes: data layout, undefined-symbol checking, branch following, patching, utility parsing, and import/export table creation.

Key responsibilities:
- `dodata()` validates data initializers, assigns small data, large data, and bss offsets, creates literal pool entries for large constants, computes `datsize`/`bsssize`, and defines linker symbols such as `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` diagnoses unresolved external references.
- `follow()` and `xfol()` reorder instruction flow to improve fall-through layout and duplicate short code runs when useful.
- `patch()` resolves branch operands to `Prog.cond`, handles unresolved dynamic branches, and collapses branch chains through `brloop()`.
- `mkfwd()` builds sparse forward links to speed PC-to-instruction lookup.
- `atolwhex()` and `rnd()` are utility parsers/rounders used by option and layout code.
- `import()` marks import symbols as undefined dynamic symbols.
- `export()` builds the `_exporttab` and `.string` data records for exported symbols and type signatures.

Implementation notes:
- Data layout favors small symbols near `REGSB` for efficient 16-bit addressing.
- Literal generation is conservative and avoids `setSB`.
- Export entries contain signature, address, and string pointer triples, terminated by zero records.
