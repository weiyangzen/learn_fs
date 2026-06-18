# sources/test-tools/fio/unittests/unittest.h

Purpose: shared declaration header for fio's CUnit test binary.

Important APIs/types: defines `struct fio_unittest_entry { const char *name; CU_TestFunc fn; }`, declares `fio_unittest_add_suite()`, and declares registration functions for lib, oslib, and cgroup suites. The cgroup registration is guarded to Linux/Android.

Control flow/state: suite arrays are expected to be NULL-terminated by `name == NULL`; `fio_unittest_add_suite()` relies on that contract.

Dependencies/integration: includes `<sys/types.h>`, CUnit core, and CUnit Basic. It is included by every unit-test implementation and the runner.

Risks/test signals: adding a new unit-test file requires adding a prototype here and a registration call in `unittest.c`. A malformed test vector without a NULL terminator can overrun memory during registration.
