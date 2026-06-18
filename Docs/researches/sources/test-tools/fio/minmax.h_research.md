# sources/test-tools/fio/minmax.h

Purpose: type-checking min/max macros and a nonzero-aware minimum helper.

Important APIs/macros: `min(x,y)`, `max(x,y)`, and `min_not_zero(x,y)`.

Control flow/state: macros capture operands into temporary typed variables, compare addresses to force compatible types at compile time, and return the selected value. `min_not_zero` treats zero as "unset" unless both are zero.

Dependencies/integration: GCC statement-expression and `__typeof__` extensions are required. Widely used in fio utility and parsing code.

Risks/test signals: operands are evaluated once, but these macros are not portable ISO C. Tests are mostly compile-time/type-safety checks plus runtime checks for zero/nonzero combinations.
