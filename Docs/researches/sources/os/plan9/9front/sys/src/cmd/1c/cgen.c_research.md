# File Research: sources/os/plan9/9front/sys/src/cmd/1c/cgen.c

Expression, lvalue, boolean, and aggregate code generator for the Plan 9 `1c` 68000 C compiler backend.

Key responsibilities:
- `cgen` emits code for scalar expressions, assignments, arithmetic, casts, calls, comparisons, increments/decrements, bitfields, conditionals, comma expressions, and address/indirect operations.
- Handles register allocation/evaluation order around function calls and complex expressions.
- Uses 68000-specific register pairs for long division/modulo and emits optimized constant multiplication/shift sequences when possible.
- `lcgen` generates lvalue addresses into address registers, stack operands, or temporaries.
- `boolgen` lowers boolean expressions and relational operators into branches or materialized 0/1 values.
- `sugen` copies or constructs structs/unions and handles aggregate returns, struct constants, `OSTRUCT`, aggregate assignment, calls returning aggregates, and conditional/comma aggregate expressions.

Important dependencies:
- Calls target helpers from `txt.c` such as `gmove`, `gopcode`, `gbranch`, `patch`, `regalloc`, `regpair`, and `regaddr`.
- Uses bitfield helpers from `swt.c`.

Notable details:
- The file carefully preserves stack argument offsets around nested calls.
- Non-interruptable temporaries through `.rathole` are explicitly warned for some struct/member cases.
