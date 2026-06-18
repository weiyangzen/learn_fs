# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-base.conf

## Purpose
This base fixture tests role type-set expansion from a base role declaration.

## Important APIs, Types, And Functions
The focused symbols are `role_check_1`, base type `role_check_1_1_t`, and ordinary roles/users/types used for complete policy context. The file assigns `role_check_1 types role_check_1_1_t`.

## Control Flow
When linked with `role-module.conf`, the same role receives an additional module type. Expansion should combine role type memberships across base and module declarations.

## State And Persistence Behavior
The policydb initially contains a role type ebitmap with one base type. Linking and expansion should mutate that role’s type set to include module-provided additions.

## Dependencies And Integration Points
It integrates with `test_role_type_set()` and `role-module.conf`.

## Risks And Edge Cases
Role membership is represented as ebitmaps indexed through `sym_val_to_name`; symbol value changes can make failures appear as wrong type sets.

## Test Signals
Expected signals are presence of `role_check_1` and a final type set containing both base and module type members after expansion.
