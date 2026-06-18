# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_role_allow_trans.conf

## Purpose
This module fixture supplies role allow and role transition declarations for hook tests.

## Important APIs, Types, And Functions
It requires `class file { read }`, declares roles `role_a_1`, `role_a_2`, `role_t_1`, `role_t_2`, type `type_rt_1`, an `allow role_a_1 role_a_2`, and a `role_transition role_t_1 type_rt_1 role_t_2`.

## Control Flow
The module is loaded and linked or used by hooks to add role relationship state into a policydb, then compared with expected policy state.

## State And Persistence Behavior
Successful processing adds role symbols, a type symbol, a role allow rule, and a role transition rule.

## Dependencies And Integration Points
It targets libsepol hook paths for role allow and role transition insertion.

## Risks And Edge Cases
The fixture has no optional blocks and no role type-set assignments, so it isolates rule insertion but not role membership validation.

## Test Signals
Expected signals are presence of both role relationship rules and successful comparison against the hook-generated policy.
