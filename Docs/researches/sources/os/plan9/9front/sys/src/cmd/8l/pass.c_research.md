# File Research: sources/os/plan9/9front/sys/src/cmd/8l/pass.c

Middle linker passes for data layout, branch patching, control-flow ordering, stack adjustment, undefined checks, and dynamic symbol table generation.

Key functions:
- `dodata` validates data initializers, groups small data, lays out data/BSS, optionally pads with BSS to an 8 KiB boundary, and defines `bdata`, `edata`, and `end`.
- `patch` resolves calls/branches to text symbols, marks unresolved dynamic imports, builds forward links via `mkfwd`, and collapses jump chains with `brloop`.
- `follow`/`xfol` reorder text to improve fallthrough, copy short instruction sequences to avoid jumps, and invert conditional branches when profitable.
- `dostkoff` computes function frame/become sizes, adjusts call frames for `BECOME`, rewrites auto/param offsets, inserts stack adjustments, and checks push/pop balance.
- `doinit` resolves data initializers referencing symbols to final constants.
- `undef` reports unresolved symbols.
- `import`, `export`, `newdata`, `undefsym`, and `ckoff` build import/export metadata for dynamic modules.
- `atolwhex` parses decimal, octal, and hex numeric command arguments.

Filesystem relevance: indirect. It lays out executable images and symbol data, not runtime filesystem code.
