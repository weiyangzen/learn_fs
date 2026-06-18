# sources/security-integrity/selinux/libsepol/src/conditional.c

Purpose: Implements conditional policy expression evaluation, node/list lifecycle, bool indexing, and binary conditional rule reading.

Important APIs and functions: `cond_optimize_lists`, `cond_expr_equal`, `cond_node_create/find/search`, `cond_evaluate_expr`, `cond_copy_expr`, `cond_normalize_expr`, `evaluate_conds`, `cond_policydb_init/destroy`, destroy helpers, `cond_init_bool_indexes`, `cond_destroy_bool`, `cond_index_bool`, `cond_read_bool`, `cond_read_list`, and `cond_av_list_search`.

Control flow: RPN expressions are evaluated on a bounded stack. Normalization removes top-level NOT by swapping true/false lists and precomputes truth tables for expressions with up to five unique booleans. Boolean updates call `evaluate_conds`, which toggles `AVTAB_ENABLED` on true/false list nodes. Binary read builds condition nodes and inserts nonunique AVTAB nodes while checking type-rule conflicts.

State and persistence: Owns condition expression/list allocations, policydb bool index arrays, and conditional avtab entries.

Dependencies and integration points: Used by policydb read, bool APIs, expansion, services, and assertion checks.

Risks: Undefined expressions disable rules. Conditional type rule conflict handling is subtle. Precompute state depends on stable bool IDs.

Test signals: Operator truth tables, stack-depth failure, bool indexing, binary reads with true/false lists, and conditional type conflicts validate it.
