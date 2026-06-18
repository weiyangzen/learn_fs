# sources/security-integrity/selinux/libsepol/include/sepol/policydb/conditional.h

Purpose: Defines internal conditional-policy expression and rule-list structures.

Important APIs and types: `cond_expr_t`, `cond_av_list_t`, `cond_node_t`; constants for RPN boolean operations, max expression depth, and precomputed bool count. Functions include expression evaluation/copy/equality/normalization, node search/create/destroy, bool indexing/read, list read/destroy, condition evaluation, AV lookup, and optimization.

Control flow: Conditional expressions are evaluated from reverse Polish notation against indexed booleans. True/false AV lists point into conditional avtab nodes whose `AVTAB_ENABLED` bit is toggled.

State and persistence: Policydb stores boolean indexes, `te_cond_avtab`, and `cond_list`. Precomputed truth tables optimize expressions with up to five unique booleans.

Dependencies and integration points: Used by boolean updates, binary policy read, expansion, and access decisions.

Risks: Stack-depth failures disable rules. Conflicting conditional type rules are rejected. Precompute assumptions depend on `COND_MAX_BOOLS`.

Test signals: Boolean changes re-enabling rules, RPN operator cases, long expressions, and binary conditional reads are critical tests.
