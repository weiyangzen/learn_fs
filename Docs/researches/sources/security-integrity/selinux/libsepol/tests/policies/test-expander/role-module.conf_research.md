# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-module.conf

## Purpose
This module adds a type to a role declared in `role-base.conf`.

## Important APIs, Types, And Functions
It requires `class file { read write }` and `role role_check_1`, declares `role_check_1_2_t`, and assigns `role role_check_1 types role_check_1_2_t`.

## Control Flow
The linker resolves the required base role, merges the module type, and expansion should combine it with the base type membership.

## State And Persistence Behavior
The module contributes one new type and one role type-set addition to the linked policydb.

## Dependencies And Integration Points
It is inspected through `test_role_type_set()` after expansion with `role-base.conf`.

## Risks And Edge Cases
If role declarations from modules are treated as separate role datums instead of merged, this fixture will expose missing or duplicate type-set state.

## Test Signals
Expected signal is `role_check_1` containing `role_check_1_2_t` in addition to the base type after expansion.
