# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/pass.c

## Scope

Middle linker passes for data layout, undefined checks, branch patching, block ordering, imports, exports, and utility parsing/alignment.

## Behavior

- `dodata()` validates initializers, separates small data, large data, and bss, aligns segments, and defines boundary symbols.
- `undef()` reports unresolved external references.
- `follow()`/`xfol()` reorder text to follow branches, copy small already-followed blocks when useful, and invert conditional branches.
- `patch()` resolves branch symbols to program pointers and collapses branch chains.
- `mkfwd()` builds skip pointers for faster PC-to-program lookup.
- `atolwhex()` parses decimal/octal/hex linker arguments.
- `import()` and `export()` build dynamic linking import/export metadata and `_exporttab` data.
- `ckoff()` validates relocation offset packing.

## Dependencies

Uses global symbol/program lists from `l.h`, `prg()`, `lookup()`, `newdata()` helpers, and dynamic relocation/import helpers.

## Risks And Invariants

- Flow reordering mutates the instruction list destructively and depends on `mark` flags.
- `brloop()` has a loop cutoff to avoid infinite branch-chain following.
- Export sorting uses simple nested loops and arena allocation, appropriate for old small symbol sets.
- Relocation offsets are constrained by fixed bit packing.
