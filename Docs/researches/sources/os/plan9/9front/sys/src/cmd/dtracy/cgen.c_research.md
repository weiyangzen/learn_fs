# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/cgen.c

This file generates dtracy VM bytecode (`DTExpr`) from typed expression AST nodes and inserts trace actions for expressions that must be evaluated in the kernel.

Key responsibilities:
- Maintains a small register allocator over 16 registers using `regsused`.
- Encodes constants with `constenc`, emitting `DTE_LDI` and `DTE_XORI` pieces.
- Generates arithmetic, bitwise, comparison, logical, ternary, cast, and variable-load bytecode in `egen`.
- Emits short branch labels and patches branch displacements after code generation.
- Builds predicate and value expressions with `codegen`.
- Converts record-marked nodes into trace actions with `tracegen`.

Important implementation notes:
- Logical operators are handled with short-circuit branch generation in `condgen` and value-producing boolean code in `condvgen`.
- `tracegen` emits `ACTTRACE` for integer runtime values and `ACTTRACESTR` for string runtime values, assigning record offsets as it walks the AST.
- Branch fixups assume an 8-bit relative offset and assert the target fits.
