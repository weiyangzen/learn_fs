<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker.c

## Purpose

Main CUnit harness for libsepol module linker behavior. It loads one base module and two policy modules, links them into `linkedbase`, also links a no-module base as `basenomods`, then delegates role, type, and conditional checks to companion files. The source was read completely for this report (155 lines).

## Important APIs, Types, and Functions

`linker_test_init()` uses `test_load_policy()` and `link_modules()` to prepare fixtures. `linker_test_cleanup()` destroys base and module policydbs. `linker_add_tests()` registers index, type, role, and conditional tests. Static wrappers call `base_*` and `module_*` helper suites.

## Control Flow

Control flow is init/load all policies, link with and without modules, then CUnit calls wrapper tests over both the unaugmented base and linked base. Cleanup destroys each policydb and frees module pointers.

## State and Persistence Behavior

Owns static `policydb_t basenomods`, `linkedbase`, and a two-element module pointer array for suite lifetime. No disk writes occur.

## Dependencies and Integration Points

Depends on libsepol `link`, `expand`, and conditional policydb APIs plus local helper/test headers and fixture policy files in `policies/test-linker`.

## Risks and Edge Cases

Risks are early init failures leaking already allocated module policydbs and test fragility to fixture symbol names. Functionally, it targets regressions in declaration copying, optional scope preservation, and symbol indexes.

## Test Signals

Test signals are successful link of module fixtures, `test_policydb_indexes()`, and companion assertions for roles, types, aliases, attributes, and conditional booleans.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.c -->
