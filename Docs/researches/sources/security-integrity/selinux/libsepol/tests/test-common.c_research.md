# sources/security-integrity/selinux/libsepol/tests/test-common.c

## Purpose
This C file provides shared CUnit assertion helpers for libsepol policydb tests. It centralizes checks for symbol scope, reverse indexes, type aliases, role type sets, and attribute type sets.

## Important APIs, Types, And Functions
Public helpers are `test_sym_presence()`, `test_policydb_indexes()`, `test_alias_datum()`, `test_role_type_set()`, and `test_attr_types()`. Internal map callbacks validate `common_datum_t`, `class_datum_t`, `role_datum_t`, `type_datum_t`, `user_datum_t`, `cond_bool_datum_t`, `level_datum_t`, and `cat_datum_t` indexes.

## Control Flow
Index tests iterate each `p->symtab[i].table` with `hashtab_map()` and assert reverse mappings such as `sym_val_to_name`, `class_val_to_struct`, and `role_val_to_struct`. Role and attribute helpers iterate positive bits in ebitmaps and compare names against expected arrays.

## State And Persistence Behavior
The file does not own persistent state. It inspects mutable `policydb_t` structures after load/link/expand operations and uses CUnit assertions to fail fast on missing required data.

## Dependencies And Integration Points
It depends on libsepol policydb internals, `hashtab_search()`, `ebitmap_for_each_positive_bit`, CUnit, and helper routines declared elsewhere. Many expander/linker tests rely on these helpers to validate in-memory structures rather than serialized policies.

## Risks And Edge Cases
Helpers compare by symbol names through value-index arrays, so corrupted reverse indexes can cascade into confusing failures. `test_sym_presence()` checks declared IDs without requiring order, but role/attribute helpers require exact set membership counts.

## Test Signals
Any CUnit failure indicates symbol scope, index, alias, role set, or attribute set inconsistency after policy processing.
