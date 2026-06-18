# sources/security-integrity/selinux/libsepol/include/sepol/policydb/constraint.h

Purpose: Defines internal policy constraint expression structures.

Important APIs and types: `constraint_expr_t` models logical and attribute/name/type-set comparisons; `constraint_node_t` binds permissions to an expression. Exports `constraint_expr_init` and `constraint_expr_destroy`.

Control flow: Constraint evaluators walk linked expressions for permission checks and validatetrans checks. This header only declares data shape and lifecycle helpers.

State and persistence: Expressions own `ebitmap_t names` and optional `type_set` names. Nodes chain per class/permission set and are serialized in policydb.

Dependencies and integration points: Depends on ebitmap and Flask types; used by policydb class data, services, and hierarchy/constraint checks.

Risks: Expression depth and operator/attribute combinations are security-sensitive because they gate permissions beyond TE rules. Destruction must release nested type sets.

Test signals: Constraint parse/read, validatetrans denial reasons, MLS constraint checks, and destroy/leak tests validate this layer.
