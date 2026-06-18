# sources/test-tools/kdevops/scripts/kconfig/expr.c

## Purpose
`expr.c` implements Kconfig expression allocation, copying, freeing, normalization, simplification, comparison, evaluation, dependency queries, and printing. It is the dependency logic substrate for menus, symbols, visibility, reverse dependencies, and help output.

## Important APIs, Types, And Functions
Allocation APIs are `expr_alloc_symbol()`, `expr_alloc_one()`, `expr_alloc_two()`, `expr_alloc_comp()`, `expr_alloc_and()`, and `expr_alloc_or()`. Lifecycle APIs are `expr_copy()` and `expr_free()`. Simplification includes `expr_eliminate_eq()`, `expr_eliminate_dups()`, `expr_transform()`, `expr_join_or()`, `expr_join_and()`, and `expr_eliminate_yn()`. Query/evaluation APIs include `expr_eq()`, `expr_contains_symbol()`, `expr_depends_symbol()`, `expr_trans_compare()`, and `expr_calc_value()`. Printing APIs include `expr_print()`, `expr_fprint()`, `expr_gstr_print()`, and `expr_gstr_print_revdep()`.

## Control Flow
Expressions are binary trees with symbol and comparison leaves. Simplification recursively descends through `&&`/`||` levels, compares leaves, replaces common operands with constant `y` or `n`, removes constant identities, folds boolean comparisons, applies De Morgan transforms, and joins redundant tristate comparisons. Evaluation recursively calculates symbol values, applies tristate `AND`/`OR`/`NOT`, and compares numeric or string values for relation nodes. Printing walks the tree with precedence checks to insert parentheses and can annotate symbols with current values in `gstr` output.

## State And Persistence
The file has no durable persistence. It allocates heap expression nodes and uses global symbols such as `symbol_yes`, `symbol_mod`, and `symbol_no` from the symbol subsystem. A static `trans_count` controls repeated simplification loops and is saved/restored around recursive equality checks.

## Dependencies And Integration Points
It depends on `lkc.h`, `xalloc`, symbol calculation/string APIs, and the `struct expr` definitions in `expr.h`. Menu and symbol code use it to represent `depends on`, `visible if`, `select`, `imply`, range, and prompt conditions.

## Risks And Test Signals
Many transforms mutate trees in place and sometimes replace nodes by structure assignment, so ownership bugs are possible if callers share expression subtrees unexpectedly. Boolean comparisons to `m` print warnings and force constants. Numeric parsing falls back to string comparison on parse failure. Tests should cover duplicate elimination, tristate truth tables, De Morgan transforms, relation comparisons across int/hex/string, printed precedence, and memory-sanitizer runs on complex dependency graphs.
