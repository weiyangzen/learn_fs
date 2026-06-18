# sources/security-integrity/selinux/libsepol/cil/src/cil_policy.c

## Purpose
`cil_policy.c` serializes a resolved CIL database to textual SELinux kernel policy language. It is an output/debug path that walks the post-processed AST/database and writes policy statements in kernel-policy order.

## Important APIs, Types, And Functions
The public entry point is `cil_gen_policy(FILE *out, struct cil_db *db)`. Key helpers gather statements (`cil_gather_statements`), format MLS levels and contexts, format conditional and constraint expressions, expand classpermissions and mapped classes, emit TE rules, emit roles/users, and emit context-labeling rules.

Major emitters include `cil_class_decls_to_policy`, `cil_commons_to_policy`, `cil_classes_to_policy`, `cil_defaults_to_policy`, `cil_default_ranges_to_policy`, `cil_sensitivities_to_policy`, `cil_categories_to_policy`, `cil_mlsconstrains_to_policy`, `cil_av_rule_to_policy`, `cil_av_rulex_to_policy`, `cil_type_rule_to_policy`, `cil_te_rules_to_policy`, `cil_roles_to_policy`, `cil_users_to_policy`, and the various `*_cons_to_policy` functions.

## Control Flow
`cil_gen_policy` initializes statement lists, gathers selected declarations while skipping abstract blocks, macros, and booleanif bodies, then emits in a fixed order: classes and SIDs, class details, defaults, MLS pieces if enabled, policy capabilities, attributes, booleans, types and TE rules, roles, users, constraints, validatetrans, SID contexts, and sorted context rules. TE rules are emitted by repeated AST walks in rule-kind order. Conditional blocks emit `if (...) { ... } else { ... }` with their nested TE rules.

## State And Persistence Behavior
The module writes to a caller-provided `FILE *`. It allocates temporary strings/lists for classperms and constraint expressions and frees them after use. It does not mutate the database except through transient allocations; however it assumes post-processing has already resolved expressions, sorted context arrays, and filled role/user/type bitmaps.

## Dependencies And Integration Points
It depends on `cil_find.c` for class expansion, `cil_list`, `cil_tree_walk`, CIL internal structs, string names from keyword globals, and system `inet_ntop` support for nodecon output. `cil.c` calls `cil_gen_policy` in the path that writes textual policy output.

## Risks And Edge Cases
The serializer assumes a valid, post-processed database. Empty classperms are skipped because kernel policy cannot represent empty permission sets. Mapped classes and permission sets are recursively expanded, so missing expression evaluation can produce wrong output. Constraint-expression string sizing is manual and vulnerable to omissions when new operand kinds are added. Text output must remain consistent with kernel policy syntax, including MLS-only statements.

## Test Signals
Golden-output tests for representative CIL policies are the strongest signal: TE rules, conditionals, map classes, permissionx ranges, MLS levels/ranges, defaults, constraints, users/roles, and every context rule type. Fuzz or sanitizer tests should stress long names, large category ranges, and empty permission expressions.
