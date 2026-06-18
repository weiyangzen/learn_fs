# sources/security-integrity/selinux/libsepol/src/optimize.c

## Purpose
Performs binary kernel policy optimization by removing AV and xperm rules that are covered by more general rules, preserving effective policy while reducing rule table size and potentially lookup cost.

## Important APIs, Types, and Functions
The public entry point is `policydb_optimize(policydb_t *p)`. Internal `struct type_vec` stores sorted type/attribute ids. `build_type_map()` maps each type or attribute to all attributes that are supersets of it. `process_avtab_datum()` subtracts covered permissions/xperms from a candidate datum. `is_avrule_redundant()`, `is_cond_rule_redundant()`, `optimize_avtab()`, `optimize_cond_av_list()`, and `optimize_cond_avtab()` remove redundant unconditional and conditional rules.

## Control Flow
`policydb_optimize()` accepts only kernel policies and rejects versions 20 through 23 where attribute gaps make optimization unsafe. It builds the type-map from `type_attr_map`/`attr_type_map`, removes redundant entries from `te_avtab`, then optimizes conditional true/false lists and removes corresponding nodes from `te_cond_avtab`. Redundancy checks search for a rule with the same class and kind whose source/target are equal or covering attributes; when a covering rule is found, covered bits are cleared from the candidate and the candidate is removed only when no bits remain.

## State and Persistence Behavior
The function mutates the in-memory policydb destructively: it unlinks `avtab` entries, frees xperm payloads, decrements `nel`, may remove empty conditional nodes, and adjusts conditional rule lists. It does not write the policy; persistence occurs only if callers later call policydb write/image functions.

## Dependencies and Integration Points
Requires a fully indexed and validated kernel `policydb_t` with populated `type_val_to_struct`, `type_attr_map`, `attr_type_map`, `te_avtab`, `te_cond_avtab`, and `cond_list`. Public API exposure comes through `sepol_policydb_optimize()` in `policydb_public.c`.

## Risks and Edge Cases
Optimization depends on sorted type vectors; `build_type_map()` appends ids in increasing loops, preserving binary-search assumptions. `process_avtab_datum()` intentionally mutates the candidate while testing coverage, so partial coverage can shrink a rule even when not fully redundant. AUDITDENY uses inverse bit logic and is sensitive to full-mask semantics. Conditional optimization moves attribute rules to the end to limit complexity, but still has nested scans. Unsupported policy versions return failure rather than leaving policy unchanged silently.

## Test Signals
Tests should compare access-vector equivalence before/after optimization, verify count reductions for redundant allow/audit/xperm rules, check partial permission subtraction, cover AUDITDENY inverse logic, verify conditional true/false deletion and empty conditional removal, and assert rejection for non-kernel and unsupported version ranges.
