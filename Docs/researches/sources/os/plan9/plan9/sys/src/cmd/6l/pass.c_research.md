# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/pass.c

## Purpose
Implements major linker passes for AMD64 `6l`: data layout, branch threading, call/branch patching, stack-frame adjustment, import/export metadata, and undefined-symbol handling.

## Key Functions
- `dodata()` lays out `SDATA` and `SBSS`, handles small data packing, alignment, `edata`, and `end`.
- `follow()` / `xfol()` reorder instruction flow, follow branches, invert conditional branches, and insert jumps when needed.
- `relinv()` maps conditional jumps to their inverse.
- `doinit()` resolves data initializers referencing symbols.
- `patch()` resolves calls and branches, builds forward links with `mkfwd()`, and collapses jump chains through `brloop()`.
- `dostkoff()` computes frame/become sizes, inserts stack adjustments, and rewrites `AUTO`/`PARAM` offsets.
- `import()` / `export()` generate dynamic import/export metadata.
- `newdata()` emits linker-side `ADATA` records for export tables.

## Important Behavior
- `follow()` is a layout optimizer: it tries to avoid branches by copying short instruction sequences and reversing conditional jumps.
- `patch()` resolves `ACALL` and `ARET` symbol references, supports `SUNDEF` dynamic references, and diagnoses unresolved or out-of-range branches.
- `dostkoff()` rewrites abstract `AADJSP` stack operations and checks balanced push/pop state around returns.
- `export()` creates `EXPTAB` plus a `.string` data symbol containing sorted exported names and signatures.

## Research Notes
This file bridges symbolic object input and addressable executable layout. It depends on instruction sizes later computed by `span.c`.
