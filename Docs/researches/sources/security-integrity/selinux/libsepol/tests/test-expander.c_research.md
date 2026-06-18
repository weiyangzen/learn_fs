<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander.c

## Purpose

This CUnit harness loads modular SELinux policy fixtures from `policies/test-expander`, links modules with libsepol, expands them into concrete `policydb_t` instances, and registers tests for expander index integrity, attribute mapping, role/user mapping, and alias preservation. It owns the shared expanded policy objects consumed by the companion expander test files. The source was read completely for this report (254 lines).

## Important APIs, Types, and Functions

`expander_policy_init()` allocates fixture paths, calls `test_load_policy()`, `link_modules()`, `policydb_init()`, and `expand_module()`, and captures the typemap returned by linking. `expander_test_init()` builds base-only, base+module, role, user, and alias fixtures. `expander_test_cleanup()` destroys every `policydb_t` and frees `typemap`. `expander_add_tests()` registers `test_expander_indexes`, `test_expander_attr_mapping`, `test_expander_role_mapping`, `test_expander_user_mapping`, and `test_expander_alias`.

## Control Flow

Initialization is fixture-driven: load base and module policy text, link optional/global declarations, expand the linked module tree, then run CUnit assertions over the resulting expanded databases. The alias test checks alias datum mapping directly; the index test delegates to the common helper.

## State and Persistence Behavior

State is process-local test state held in global/static `policydb_t` variables and a `uint32_t *typemap`. No persistent storage is written, but cleanup must mirror initialization or later suites can observe leaked policydb state.

## Dependencies and Integration Points

Depends on libsepol `policydb`, `expand`, `link`, and conditional headers, plus local `parse_util`, `helpers`, and companion expander test headers. It integrates with the repository CUnit runner through `expander_test_init`, `expander_add_tests`, and `expander_test_cleanup`.

## Risks and Edge Cases

Important risks are fixture path allocation failures, early-return cleanup gaps during init, and regressions in optional block expansion that preserve symbols in the linked module but drop them during expansion. The variable-length filename array also relies on `num_modules` being small and controlled by tests.

## Test Signals

Strong test signals are the registered CUnit cases, successful load/link/expand of all fixture policy combinations, `test_policydb_indexes()`, and exact assertions in the companion role/user/attribute files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.c -->
