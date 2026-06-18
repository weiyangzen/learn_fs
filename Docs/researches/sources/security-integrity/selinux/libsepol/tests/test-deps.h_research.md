# sources/security-integrity/selinux/libsepol/tests/test-deps.h

## Purpose
This header exposes dependency-test suite hooks to the libsepol CUnit runner.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `deps_test_init()`, `deps_test_cleanup()`, and `deps_add_tests(CU_pSuite suite)`.

## Control Flow
The runner uses these functions to load base fixtures, register dependency test cases, and release policydb state.

## State And Persistence Behavior
No state is declared here; static policydb arrays live in `test-deps.c`.

## Dependencies And Integration Points
It follows the common suite interface used by other test headers in this directory.

## Risks And Edge Cases
Changing names or signatures would disconnect the dependency suite from the runner.

## Test Signals
Compilation and successful CUnit test registration are the direct signals.
