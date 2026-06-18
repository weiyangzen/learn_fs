# File Research: sources/os/plan9/9front/sys/src/cmd/cc/cc.h

Purpose: Central shared header for the Plan 9 C compiler front end.

Key points:
- Includes Plan 9 system headers, `compat.h`, and links against `../cc/cc.a$O`.
- Defines core structs: `Node`, `Sym`, `Decl`, `Type`, `Io`, `Hist`, `Term`, `Bits`, `Spec`, `Funct`, and `Init`.
- Defines AST operation enum `O*`, type enum `T*`, declaration class enum `C*`, type qualifier/garbage flags `G*`, and bit masks for type/class combinations.
- Declares compiler-wide globals for symbol tables, type tables, parser state, include stack, debug flags, output buffers, offsets, declaration stack, and target settings.
- Declares front-end APIs grouped by parser, lexer, macro handling, declarations, semantic analysis, constant folding, function overloading, tree utilities, Acid output, pickle output, bitsets, pragma checks, code generation hooks, 64-bit lowering, and machine capability checks.
- Defines custom format checker pragmas for compiler diagnostics.

Dependencies and interactions:
- Included by all files in `cmd/cc`.
- Machine-specific compilers provide code generation hooks such as `codgen`, `gextern`, `align`, `maxround`, and `machcap`.
- Parser tokens come from generated yacc output for `cc.y`.

Research notes:
- This is the front-end contract between parser, semantic analysis, declarations, diagnostics, and target back ends.
- Many globals are declared through `EXTERN`, making inclusion context important.
