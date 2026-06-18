# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-global.conf

## Purpose
This module validates global role requirements and role allow linking.

## Important APIs, Types, And Functions
It requires `role role_req_r, user_r`, declares marker `mod_global_t`, creates `a_t`, and emits `allow role_req_r user_r`. A role-type assignment for `role_req_r` is intentionally commented out.

## Control Flow
The dependency suite links this fixture into positive and negative bases. The required roles must be found before the role allow rule can be accepted.

## State And Persistence Behavior
Successful linking adds module declaration state and a role allow relationship to the base policydb. Failed linking should produce no enabled marker declaration.

## Dependencies And Integration Points
It integrates role symbol scope, role allow rule parsing, and module global require resolution.

## Risks And Edge Cases
The fixture does not test role type-set mutation for the required role because that line is commented. It therefore isolates role require plus role allow, not role membership.

## Test Signals
Expected signals are success only when both roles exist and enabled `mod_global_t` in the positive case.
