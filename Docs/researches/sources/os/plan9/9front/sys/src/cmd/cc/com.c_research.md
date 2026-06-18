# File Research: sources/os/plan9/9front/sys/src/cmd/cc/com.c

Purpose: Performs semantic type checking, expression rewriting, comma hoisting, simplification, constant folding, and comparison diagnostics.

Key points:
- `complex` is the main pipeline: type complexing with `tcom`, comma normalization, rewrite simplification with `ccom`, constant/address analysis via `acom`, and target lowering via `xcom`.
- `tcomo` handles type checking and type assignment for assignments, arithmetic, shifts, comparisons, logical operators, casts, return, function calls, names, strings, address/deref, dot access, `sizeof`, `signof`, and constructors.
- Inserts casts for assignment, return, arguments, array/function-to-pointer conversion, and promotions.
- Checks lvalues, void/incomplete types, pointer arithmetic, function prototypes, argument count/type, divide by zero, invalid shifts, address of bitfield/register, and undeclared functions/names.
- `tcoma` checks function argument lists against prototypes.
- `tcomd` resolves struct/union member access.
- `tcomx` checks struct constructor initializers.
- Comma handling hoists comma operators while preserving short-circuit and conditional semantics.
- `ccom` rewrites no-op casts, address/deref pairs, constant conditionals, arithmetic identities, zero checks, commutative constant folding, and constant expressions.
- `compar` warns about useless or misleading integer comparisons based on inferred type ranges.

Dependencies and interactions:
- Uses type compatibility tables and helper functions declared in `cc.h`.
- Calls `dpcheck` for format-string checking.
- Relies on machine hooks such as `machcap`, `xcom`, and constant conversion helpers.
- Produces trees suitable for code generation.

Research notes:
- This is the central semantic pass for expressions.
- It intentionally includes warnings for C pitfalls such as misleading unsigned comparisons and 32-bit complement casts extended to 64 bits.
