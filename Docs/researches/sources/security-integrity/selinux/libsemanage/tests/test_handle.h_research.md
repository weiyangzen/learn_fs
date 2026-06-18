# sources/security-integrity/selinux/libsemanage/tests/test_handle.h

## Purpose
Declares the handle CUnit suite interface.

## APIs and integration
Exports `handle_test_init()`, `handle_test_cleanup()`, and `handle_add_tests(CU_pSuite)`.

## Risks
No persistent state, but the declarations must remain aligned with `DECLARE_SUITE(handle)`.
