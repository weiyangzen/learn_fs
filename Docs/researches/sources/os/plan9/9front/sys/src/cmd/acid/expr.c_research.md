# File Research: sources/os/plan9/9front/sys/src/cmd/acid/expr.c

Expression evaluator dispatch table and implementations for Acid operators.

Key responsibilities:
- Defines format sizes and `fmtsize()`.
- Evaluates constants, names, casts, eval, list expressions, pointer indirection, frame-local address lookup, indexing, list head/tail/append/delete, assignment, arithmetic, comparisons, bitwise/logical operators, increments/decrements, calls, format override, and whatis.
- Reads memory for `*`, symbol memory for `@`, and indexed pointer arithmetic.
- Implements string concatenation and string-plus-rune.
- Implements list concatenation and scalar append-to-list.
- Dispatches expression opcodes via `expop[]`.

Important behavior:
- Integer pointer increments/decrements advance by `fmtsize()` for the value’s current format.
- `i`/`I` format size is architecture instruction size from machdata.
- `OCALL` defaults to empty list return, dispatches builtin when forced or when no user proc exists, otherwise invokes `call()`.
- Equality supports ints, floats, strings, and recursive lists.

Dependencies:
- Uses memory access, list helpers, string helpers, machdata, `odot()`, `oframe()`, and builtins.

Notable risks:
- Some arithmetic preserves lhs format even when result type changes.
- Division checks integer and int/float zero, but float/int division does not check zero integer divisor.
