# sources/security-integrity/selinux/libsepol/src/hierarchy.c

Purpose: enforces SELinux hierarchical namespace bounds for types, roles, and users. It can infer parent bounds from dotted names, expand parent allow rules, compare child permissions against parent coverage, and report violations.

Important APIs and functions: public functions are `bounds_check_type`, `bounds_check_types`, `bounds_check_roles`, `bounds_check_users`, `bounds_destroy_bad`, `hierarchy_add_bounds`, and `hierarchy_check_constraints`. Internal helpers build parent global/conditional AV tabs (`bounds_expand_parent_rules`), check child global/conditional rules (`bounds_check_child_rules`), identify uncovered permissions (`bounds_not_covered`), and report bad AV entries (`bounds_report`).

Control flow: type checking first expands all rules where a parent type participates into a temporary global AV tab plus per-conditional true/false tables. It then walks child rules and verifies that each allowed permission is covered by the parent rule, accounting for bounded target types. Role and user checks are simpler ebitmap containment checks against parent roles/types. `hierarchy_add_bounds` derives missing bounds from dotted identifiers by stripping the final component and looking up the parent. `hierarchy_check_constraints` adds inferred bounds, runs user/role/type checks, and returns `SEPOL_ERR` on violations.

State and persistence behavior: no disk persistence. The code mutates `bounds` fields when inferring hierarchy parents. It allocates temporary avtabs and bad-node lists that must be destroyed. Errors are reported through the handle.

Dependencies and integration points: depends on policydb, conditional rules, avtab, expand, util, ebitmap, hashtab, and `debug.h`. `expand_module` calls `hierarchy_check_constraints` when requested after building output type/attribute maps.

Risks: checks are security-sensitive because a child type, role, or user must not gain authority beyond its parent. Temporary AV tab construction for conditionals must correctly account for permissions common to true and false branches. Dotted-name inference mutates policy state and can convert naming mistakes into orphan errors. Failure cleanup around partially allocated `bounds_cond_info` must remain correct.

Test signals: policies with valid and violating type bounds, bounded target types, role and user containment failures, conditional allow rules with permissions in one or both branches, dotted-name inferred parents, orphan dotted identifiers, empty rule sets, and memory-failure paths in temporary AV tab/list allocation.
