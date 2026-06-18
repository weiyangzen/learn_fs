# sources/security-integrity/selinux/checkpolicy/policy_define.h

## Purpose

`policy_define.h` declares the parser semantic action API implemented by `policy_define.c`. It is included by the yacc grammar and exposes one function per major SELinux policy language construct. The header is the grammar-to-implementation contract.

## Important APIs and Constants

`COND_ERR` is a sentinel `avrule_t *` value used by yacc actions for conditional rule failures, because `NULL` can represent an empty valid conditional rule list. `TRUE` and `FALSE` are local boolean constants.

The declarations cover conditional AV rule construction (`define_cond_*`), conditional expressions (`define_cond_expr()`), class and permission definitions, booleans/tunables, MLS sensitivity/category/level definitions, constraints, type/role/user declarations, all major TE/RBAC rules, object-context declarations, policy capabilities, permissive and neveraudit flags, and queue insertion helpers (`insert_id()`, `insert_separator()`).

## Control Flow and Integration

`policy_parse.y` calls these functions in grammar reductions after tokens have been queued. Some functions return `int` for direct success/failure, some return allocated or sentinel `avrule_t *`/`cond_expr_t *` values used by conditional grammar productions, and `define_cexpr()` uses `uintptr_t` because yacc carries constraint-expression pointers through an integer-compatible union field.

## State and Persistence Behavior

The header itself is stateless. Its functions operate on global parser state (`policydbp`, `id_queue`, `pass`, `mlspol`, line globals) and mutate the policydb. The queue helper APIs define the shared ordering contract: callers insert identifiers either at tail or head and use NULL separators to delimit logical sets.

## Dependencies and Risks

Because the header does not include every libsepol type it mentions, it assumes includers have already pulled in policydb/conditional definitions. Return-value conventions are mixed and parser-specific; incorrect yacc action checks can confuse an empty construct with an error, especially around `COND_ERR`. Any signature change must be coordinated with grammar `%type` declarations in `policy_parse.y`.

## Test Signals

Compilation of the generated parser is the first signal. Behavioral tests should map grammar productions to the correct function calls and verify that sentinel returns abort only when intended.
