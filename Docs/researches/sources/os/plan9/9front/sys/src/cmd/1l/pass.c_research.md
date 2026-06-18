# File Research: sources/os/plan9/9front/sys/src/cmd/1l/pass.c

Linker layout, branch following, stack-offset rewriting, and unresolved-symbol passes for `1l`.

Key responsibilities:
- `dodata` validates data initializers, lays out small data first, then regular data, optional BSS/data packing, BSS, and defines `bdata`, `edata`, and `end`.
- `patch` resolves subroutine calls and branch offsets to `pcond` pointers, reports undefined symbols, and collapses branch chains.
- `mkfwd` builds skip-forward links for faster PC-to-instruction lookup.
- `follow` and `xfol` reorder instruction flow to improve fallthrough, avoid some branches, copy short instruction sequences, and invert conditional branches when useful.
- `relinv` maps conditional branches to their inverse, including FP branches.
- `dostkoff` computes stack offsets, inserts stack adjustments where control-flow stack states merge, rewrites auto/param offsets, expands pseudo/synthetic operations, and lowers long multiply/divide calls to helper routines when needed.
- `atolwhex` parses decimal/octal/hex numeric options.
- `undef` reports unresolved external references.
- `initmuldiv1` marks helper routines as required; `initmuldiv2` locates their `ATEXT` records.

Notable details:
- Return instructions with nonzero stack offset are rewritten to adjust stack before `RTS`.
- Some operations, such as `MOVW CCR`, `EXTBL`, and long mul/div, are expanded into helper sequences before final span/assembly.
