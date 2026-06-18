<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c

## Purpose

Verifies RBAC role symbols and role type sets after base-only and base-plus-module linking, including optional declarations and additive role type-set contributions. The source was read completely for this report (232 lines).

## Important APIs, Types, and Functions

`only_dominates_self()` walks each role dominance bitmap. `base_role_tests()` validates base/global and base/optional roles. `module_role_tests()` validates module roles and additive type-set placement across global and optional declaration scopes.

## Control Flow

Each case finds declaration IDs by tag, asserts role symbol scope, validates role type sets through `test_role_type_set()`, and confirms dominance does not gain unexpected role relationships.

## State and Persistence Behavior

No state is stored by this file; it reads caller-owned policydbs.

## Dependencies and Integration Points

Depends on libsepol policydb/link headers, CUnit, and local helper functions for declaration lookup and role type-set checking.

## Risks and Edge Cases

Key risks are incorrect unioning of role type sets, misplaced optional declaration data, and accidental dominance expansion beyond self-dominance.

## Test Signals

Test signal comes from exact role symbol presence, type-set contents, and dominance bitmap checks for both base and linked module databases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c -->
