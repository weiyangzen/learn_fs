# sources/security-integrity/selinux/libsemanage/tests/test_ibendport.h

## Purpose
Declares the InfiniBand endport CUnit suite interface.

## APIs and integration
Exports `ibendport_test_init()`, `ibendport_test_cleanup()`, and `ibendport_add_tests(CU_pSuite)`.

## Risks
No runtime state. Names must remain synchronized with `DECLARE_SUITE(ibendport)` in the runner.
