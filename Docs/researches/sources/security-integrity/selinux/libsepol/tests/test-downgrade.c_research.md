# sources/security-integrity/selinux/libsepol/tests/test-downgrade.c

## Purpose
This CUnit suite tests backward compatibility of binary policy writing by repeatedly downgrading a high-version policy and reading it back.

## Important APIs, Types, And Functions
Key functions are `downgrade_test_init()`, `downgrade_test_cleanup()`, `downgrade_add_tests()`, `test_downgrade()`, `do_downgrade_test(int mls)`, `read_binary_policy()`, and `write_binary_policy()`. Constants are `POLICY_BIN_HI` and `POLICY_BIN_LO`.

## Control Flow
`test_downgrade()` runs non-MLS and MLS downgrade loops. `do_downgrade_test()` reads `policy.hi`, toggles `policydb.mls`, then for each high version writes lower versions down to `POLICYDB_VERSION_MIN` and reads each generated `policy.lo` back into a temporary policydb.

## State And Persistence Behavior
The suite owns a static `policydb`. It writes `policies/test-downgrade/policy.lo` repeatedly as a test artifact and reads it back. It suppresses libsepol warning output while writing through a temporary `sepol_handle_t`.

## Dependencies And Integration Points
It depends on `policydb_read()`, `policydb_write()`, `struct policy_file`, policy version constants, standard file I/O, and CUnit.

## Risks And Edge Cases
The test mutates and reuses a global policydb. Early returns after initializing `policydb_tmp` can leak temporary state. MLS downgrades before `POLICYDB_VERSION_MLS` are expected write failures and must remain special-cased.

## Test Signals
Signals are successful write/read round trips for each supported lower version and expected skips for unsupported MLS-to-pre-MLS downgrades.
