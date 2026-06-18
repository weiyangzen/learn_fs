# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/small-base.conf

## Purpose
This base fixture backs the main expander module matrix. It defines attributes and optional blocks arranged to test type-attribute expansion across global, enabled optional, and disabled optional scopes.

## Important APIs, Types, And Functions
Important symbols include `attr_check_base_1` through `attr_check_base_11`, optional attributes `attr_check_base_optional_*`, disabled optional attributes, `base_t`, many `attr_check_base_*_t` types, and optional blocks requiring either real attributes/module types or `does_not_exist_t`.

## Control Flow
The base declares some attributes and type memberships globally, some in optional blocks that should be enabled by the module, and some in optional blocks that should remain disabled. It also provides booleans used by module conditional expressions.

## State And Persistence Behavior
Expansion should produce accurate attribute member ebitmaps for attributes sourced from the base, module, and optional declarations. Disabled optionals should not leak memberships into active expanded state.

## Dependencies And Integration Points
It pairs with `test-expander/module.conf` and common helpers that inspect attribute membership, policydb indexes, and conditional maps.

## Risks And Edge Cases
The naming scheme is the contract. Small edits to numbers or optional requirements can break several expected mapping categories at once.

## Test Signals
Expected signals are enabled optional blocks when their requirements are satisfied by the module, disabled blocks when `does_not_exist_t` is required, and exact type sets for each test attribute.
