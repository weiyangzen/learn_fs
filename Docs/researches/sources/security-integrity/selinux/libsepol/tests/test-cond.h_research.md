# sources/security-integrity/selinux/libsepol/tests/test-cond.h

## Purpose
This header exposes the conditional-expression test suite hooks to the libsepol CUnit runner.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `cond_test_init()`, `cond_test_cleanup()`, and `cond_add_tests(CU_pSuite suite)`.

## Control Flow
The runner calls the init hook before suite execution, `cond_add_tests()` to register `cond_expr_equal`, and cleanup after execution.

## State And Persistence Behavior
The header owns no state; the static policydbs live in `test-cond.c`.

## Dependencies And Integration Points
It integrates the conditional suite with the common CUnit suite registration pattern used by libsepol tests.

## Risks And Edge Cases
Signature drift here breaks test runner integration even if the implementation still compiles standalone.

## Test Signals
Compilation and successful suite registration are the header-level signals.
