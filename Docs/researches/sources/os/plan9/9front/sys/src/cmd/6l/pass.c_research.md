# File Research: sources/os/plan9/9front/sys/src/cmd/6l/pass.c

- Role: Middle linker passes: data layout, branch patching/following, stack-frame rewrite, import/export tables, and undefined checks.
- `dodata()` validates DATA records, lays out small data first, then remaining data, optionally pads with BSS under debug `j`, lays out BSS, and defines `edata`/`end`.
- `patch()` builds forward links, resolves call/jump symbols to text or imports, converts offsets to branch targets, and follows jump chains.
- `follow()`/`xfol()` reorder code by following branches, invert conditional branches where profitable, and copy short instruction runs to reduce jumps.
- `dostkoff()` computes per-function frame/become sizes, inserts stack adjust pseudo-ops, rewrites AUTO/PARAM offsets to SP-relative output form, tracks push/pop deltas, and rewrites special `RET const` become forms into stack-adjust plus jump.
- `doinit()` resolves data initializers that reference static/extern symbols.
- `import()` marks unresolved imported symbols as `SUNDEF` and assigns relocation/import indices.
- `export()` builds `_exporttab` and `.string` DATA records containing signatures, addresses, and names of exported symbols.
- Utility functions include `brchain()`, `relinv()`, `mkfwd()`, `brloop()`, `atolwhex()`, `undef()`, `ckoff()`, and local `newdata()`.
