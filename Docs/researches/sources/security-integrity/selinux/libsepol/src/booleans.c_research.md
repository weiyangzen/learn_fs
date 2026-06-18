# sources/security-integrity/selinux/libsepol/src/booleans.c

Purpose: Implements public policydb operations for booleans.

Important APIs and functions: `sepol_bool_set`, `sepol_bool_count`, `sepol_bool_exists`, `sepol_bool_query`, and `sepol_bool_iterate`; internal `bool_update` and `bool_to_record`.

Control flow: Updates duplicate the key name, find the `cond_bool_datum_t` in `p_bools`, validate value 0/1, mutate `state`, then `sepol_bool_set` calls `evaluate_conds` to toggle conditional rule enable bits. Query/iterate convert indexed bool datums to public records.

State and persistence: Mutates `policydb->p_bools` datum state and conditional AV rule state. Records returned to callers are heap-owned copies.

Dependencies and integration points: Uses internal policydb/hashtab/conditional structures, public boolean records, debug/handle helpers.

Risks: If conditional reevaluation fails after state mutation, caller receives error but state may already be changed. Iteration assumes indexed bool arrays are current.

Test signals: Set valid/invalid values, observe conditional AV changes, query missing booleans, and iterator callback stop/error coverage.
