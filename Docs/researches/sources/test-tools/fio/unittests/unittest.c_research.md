# sources/test-tools/fio/unittests/unittest.c

Purpose: main CUnit test runner for fio unit tests.

Important APIs/functions: `fio_unittest_add_suite()` wraps `CU_add_suite()` and iterates a NULL-terminated `fio_unittest_entry` array to add tests. `fio_unittest_register()` exits on registration failure. `main()` initializes the CUnit registry, registers all lib/oslib suites and platform cgroup suite, runs tests in verbose basic mode, cleans up, and returns the CUnit error code.

Control flow/state: failures during suite creation clean up the CUnit registry immediately. Registration order is fixed and mirrors prototypes in `unittest.h`.

Dependencies/integration: depends on CUnit Basic, all suite registration functions, and Linux/Android guards for cgroup tests.

Risks/test signals: if a suite function has unresolved production dependencies, the entire binary fails to link. Returning `CU_get_error()` after `CU_basic_run_tests()` reports framework errors rather than necessarily failed assertions, so CI integration must inspect CUnit behavior. Tests should verify nonzero exit on failed registration.
