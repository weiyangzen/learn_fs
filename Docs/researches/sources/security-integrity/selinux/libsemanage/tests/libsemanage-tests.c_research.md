# sources/security-integrity/selinux/libsemanage/tests/libsemanage-tests.c

## Purpose
Main CUnit runner for libsemanage unit tests.

## Control flow
`DECLARE_SUITE` registers each suite with init/cleanup and add-tests functions. `do_tests()` initializes CUnit, registers store, utilities, handle, boolean, fcontext, iface, ibendport, node, port, user, and other suites, selects basic verbose/normal or console mode, runs tests, and returns success only when CUnit has no error and zero failed tests. `main()` parses `-v/--verbose` and `-i/--interactive`.

## Dependencies and risks
Depends on every suite header and CUnit Basic/Console APIs. Verbose defaults to enabled. A suite registration failure cleans up and propagates CUnit errors.
