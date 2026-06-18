# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/mul.c

This file implements multiply-by-constant strength reduction for the SPARC C compiler backend. It searches for compact shift/add/subtract instruction sequences and caches results in `multab`.

The encoded sequence language uses letters for shifts and `+`/`-` operations with small register-selection digits. `docode()` validates and expands candidate hints against a target multiplier. `gen1()`, `gen2()`, and `gen3()` recursively search sequences up to a small length.

`mulcon0()` handles negative multipliers, cache lookup, exception hint-table lookup, recursive factorization by powers of two, and search fallback. The large `hintab[]` records constants the search would otherwise miss or handle poorly.

This optimization is called from switch/code generation through `mulcon()` in `swt.c`. It trades compiler complexity for faster generated integer multiplication on SPARC hardware where general multiply may be expensive.
