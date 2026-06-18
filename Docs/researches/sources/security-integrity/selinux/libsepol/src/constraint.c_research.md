# sources/security-integrity/selinux/libsepol/src/constraint.c

Purpose: Implements lifecycle helpers for policy constraint expressions.

Important APIs and functions: `constraint_expr_init` zeroes a `constraint_expr_t`, initializes its names ebitmap, allocates `type_names`, and initializes the type set. `constraint_expr_destroy` walks a linked expression list and frees names, type sets, and nodes.

Control flow: Init prepares a single expression node for parser/read use. Destroy handles an entire linked expression chain.

State and persistence: Each expression owns an ebitmap and allocated `type_set_t`; constraints are attached to class datums and serialized in policydb.

Dependencies and integration points: Depends on policydb, constraint, expand/type-set helpers, and Flask types.

Risks: If `type_names` allocation fails after ebitmap init, caller must handle partially initialized state. Destroy assumes nodes are heap allocated.

Test signals: Init failure paths, destroy of multi-node expressions, constraints using name and type-set operands, and leak checks validate it.
