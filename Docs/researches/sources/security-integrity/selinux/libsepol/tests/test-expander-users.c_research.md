<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-users.c

## Purpose

Validates user-to-role mapping after expansion by walking the expanded user role bitmap and comparing it with expected role names. The source was read completely for this report (77 lines).

## Important APIs, Types, and Functions

`check_user_roles()` locates a `user_datum_t`, allocates a found-count array, iterates `user->roles.roles` with `ebitmap_for_each_positive_bit`, maps role values through `p_role_val_to_name`, and asserts exact role coverage. `test_expander_user_mapping()` applies it to `user_check_1`.

## Control Flow

The helper fails fast for missing users or allocation failure, counts every positive role bit, checks each expected role is found exactly once, and asserts there are no extra roles.

## State and Persistence Behavior

Uses only stack and temporary heap state; the external `policydb_t user_expanded` owns all policy structures.

## Dependencies and Integration Points

Depends on libsepol user/role policydb internals, ebitmap iteration, CUnit, and the expander fixture initialized elsewhere.

## Risks and Edge Cases

Risks include off-by-one role value/name mapping and fixture drift. The test intentionally catches both missing and extra roles, so unexpected role inheritance is visible.

## Test Signals

The main test signal is exact bitmap-to-name verification for the expanded user fixture.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.c -->
