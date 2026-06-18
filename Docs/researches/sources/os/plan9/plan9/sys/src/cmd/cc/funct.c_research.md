# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/funct.c

This file supports Plan 9 `typestr` operator/function rewriting, effectively a compiler extension for struct/union-like operator hooks.

Key behavior:
- `dclfunct()` recognizes eligible type tags, synthesizes external declarations for operation helper functions, and records them in a `Funct` table on the type.
- `isfunct()` rewrites arithmetic, comparison, unary, assignment-op, and cast AST nodes into `OFUNC` calls to generated helper symbols.
- Tables map C operators to helper suffixes such as `add`, `eq`, `asadd`, `neg`, and built-in scalar cast suffixes.

Important details:
- Binary operators become calls like `T f(T,T)`, comparisons become `int f(T,T)`, assignment ops become address-taking calls, and casts use `_scalarT_` / `T_scalar_` naming.
- Normal structure assignment is left to the compiler and not rewritten through this path.
- Rewriting includes type compatibility checks against the generated helper prototype.

Filesystem relevance:
- Indirect compiler extension support.
