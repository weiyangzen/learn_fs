# File Research: sources/virtualization/spdk/lib/ut/ut.c

This file implements SPDK’s common unit-test runner around CUnit.

It supports built-in options `--test/-t`, `--suite/-s`, `--list/-l`, and `--help/-h`, and can merge caller-provided long options, short option string, option callback, init callback, and usage callback through `spdk_ut_opts`.

`parse_args()` builds the combined option table and optstring, validates maximum option counts and optstring size, records selected test/suite/action, and dispatches unknown recognized options to the caller callback. Tests run by default.

`run_tests()` validates requested suite and/or test names. If a test is selected without a suite, it allows that only when exactly one suite is registered. It configures CUnit to abort on framework errors and run in verbose basic mode, then runs one test, one suite, or all tests. The return value is the number of CUnit failures.

`list_tests()` prints all registered suites and test cases. `spdk_ut_run_tests()` is the exported entry point: parse arguments, print help/list, call optional init callback before running tests, and return a process-style status.

Key invariants are correct ownership of caller-supplied option arrays, no dynamic allocation, and returning nonzero for invalid CLI usage or test failures. The code uses CUnit’s one-based suite/test positional API.
