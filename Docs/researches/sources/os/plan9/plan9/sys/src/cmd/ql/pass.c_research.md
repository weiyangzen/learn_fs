# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/pass.c

Mid-level linker passes for data layout, branch patching, control-flow following, and dynamic export/import table generation.

Key functions:
- `dodata()` validates data initializers, assigns small data first, lays out data and BSS, builds literal data entries for large constants/address constants, and defines `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` diagnoses unresolved external references.
- `relinv()` maps conditional branches to inverse conditions.
- `patch()` resolves branch and call symbol operands to `Prog.cond` targets, handles undefined calls through `UP`, then collapses branch chains with `brloop()`.
- `mkfwd()` creates sparse forward links to accelerate PC target lookup.
- `follow()`/`xfol()` reorder code by following branches, copying short instruction runs when useful, and inserting synthetic branches when needed.
- `atolwhex()` parses decimal, octal, and hex numeric arguments.
- `rnd()` rounds addresses.
- `import()` turns unresolved signature-bearing symbols into import entries.
- `export()` builds `_exporttab` and `.string` data containing sorted exported symbol signatures, addresses, and names.

Risk/notes:
- `dodata()` mutates symbol types between `SDATA`, `SDATA1`, and `SBSS`; this layout is consumed by `span()` and assembly output.
- `xfol()` duplicates already-followed code in limited cases to improve fall-through layout.
- Export table construction emits synthetic `ADATA` records into `datap`.
