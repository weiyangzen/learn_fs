# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/module.conf

## Purpose
This is the main expander module fixture. It stress-tests conditional mapping, optional block enablement, and type-to-attribute expansion across base and module declarations.

## Important APIs, Types, And Functions
The module requires base booleans `allow_ypbind`, `secure_mode`, and `allow_execstack`, base types `system_t` and `sysadm_t`, `class file`, and several base attributes. It declares `module_1_bool`, optional `module_1_bool_2`, `module_t`, `attr_check_mod_1` through `attr_check_mod_11`, multiple optional module attributes, and many `typeattribute` relationships.

## Control Flow
The global conditional rule depends on a conjunction of module and base booleans. Optional blocks are deliberately split between satisfied requirements (`base_t`, existing attributes) and unsatisfied requirements (`does_not_exist_t`) to test enabled and disabled declaration expansion.

## State And Persistence Behavior
Successful link/expand should merge type-attribute memberships from global, base optional, module optional, disabled base optional, and disabled module optional contexts into the expected expanded ebitmaps. Disabled optional blocks should not contribute active membership.

## Dependencies And Integration Points
This module pairs with `test-expander/small-base.conf` and common helpers such as `test_attr_types()` to inspect attribute membership after expansion.

## Risks And Edge Cases
The file encodes a dense matrix by naming convention. Renaming an attribute or moving a declaration between global and optional scope can invalidate multiple expected mappings.

## Test Signals
Strong signals are correct enabled/disabled optional declarations, correct expanded attribute member sets, and preserved conditional expression mapping for the complex boolean expression.
