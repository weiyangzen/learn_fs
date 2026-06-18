# sources/security-integrity/selinux/libsepol/src/assertion.c

Purpose: Implements neverallow and neverallowxperm assertion checking against expanded policy AV tables.

Important APIs and functions: Public `check_assertion(policydb_t *p, const avrule_t *narule)` and `check_assertions(sepol_handle_t *handle, policydb_t *p, const avrule_t *avrules)`. Internals match class permissions, compare extended-permission forms, compute violated xperms, scan avtabs/conditional lists, and report failures with source line information.

Control flow: For each neverallow rule, type sets and class-permission nodes are expanded/matched against allowed rules in `te_avtab` and conditional rules. Violations are formatted with type/class/permission names and counted as errors.

State and persistence: No persistent state is created. It reads policydb indexes, type attribute maps, AV tables, conditional lists, and rule metadata.

Dependencies and integration points: Depends on avtab, policydb, expand, util, private/debug helpers. Called during module expansion/checking and fuzzing.

Risks: This is security-critical: missed matches allow invalid policy; false positives block valid policy. Extended permission and conditional conflict logic is complex.

Test signals: Positive/negative neverallow and neverallowxperm policies, conditionals, attributes, source-line diagnostics, and fuzz coverage validate it.
