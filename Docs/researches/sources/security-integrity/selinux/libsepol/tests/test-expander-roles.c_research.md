<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c

## Purpose

Checks that role-to-type mappings survive module expansion for the role-specific expander fixture. The source was read completely for this report (38 lines).

## Important APIs, Types, and Functions

Exports `test_expander_role_mapping()`, which expects `role_check_1` to map to `role_check_1_1_t` and `role_check_1_2_t` via `test_role_type_set()`.

## Control Flow

The test reads the externally initialized `role_expanded` policydb and performs one focused role type-set assertion.

## State and Persistence Behavior

No storage is owned; it consumes the global `policydb_t role_expanded` built by `expander_test_init()`.

## Dependencies and Integration Points

Depends on `helpers.h`, `test-common.h`, CUnit, and libsepol policydb types.

## Risks and Edge Cases

Small fixture breadth means it is a regression tripwire for basic role expansion, not exhaustive RBAC behavior.

## Test Signals

Passing CUnit output confirms the expected role type bitmap was mapped in the expanded policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c -->
