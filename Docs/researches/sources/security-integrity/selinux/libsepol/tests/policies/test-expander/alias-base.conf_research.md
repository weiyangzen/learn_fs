# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-base.conf

## Purpose
This expander fixture tests how type aliases declared in a base policy and optional base blocks survive module expansion.

## Important APIs, Types, And Functions
Important symbols are `enable_optional`, `alias_check_1_t`, `alias_check_2_t`, `alias_check_3_t`, aliases `alias_check_1_a` and `alias_check_2_a`, and an optional block requiring `alias_check_3_a`. It also defines normal roles, users, booleans, SID, fs_use, and genfscon scaffolding.

## Control Flow
The base declares a direct alias, an alias inside an enabled optional block, and an optional block whose requirement is satisfied by a module-provided alias from `alias-module.conf`.

## State And Persistence Behavior
After link and expansion, alias datums should map to the correct primary type and flavor. Optional alias declarations should contribute only when their requirements are satisfied.

## Dependencies And Integration Points
The fixture pairs with `alias-module.conf` and `test_alias_datum()` from `test-common.c`, which checks `TYPE_ALIAS` or primary-type layout.

## Risks And Edge Cases
Alias values and primary references are subtle in expanded policydbs. Reordering or changing optional alias requirements can alter whether aliases are retained as aliases or collapsed into primary type datums.

## Test Signals
Expansion should preserve expected alias-to-primary relationships and enable the module-dependent optional block when `alias_check_3_a` exists.
