# sources/security-integrity/selinux/libsemanage/tests/test_bool.h

## Purpose
Declares the boolean CUnit suite interface.

## APIs and integration
Exports `boolean_test_init()`, `boolean_test_cleanup()`, and `boolean_add_tests(CU_pSuite)`. Includes CUnit Basic and public semanage header so the runner can register the suite.

## Risks
No state here; suite naming must match `DECLARE_SUITE(boolean)` in the test runner.
