# sources/security-integrity/selinux/libsemanage/tests/test_utilities.h

## Purpose
`test_utilities.h` declares CUnit lifecycle hooks for the libsemanage utilities test suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `semanage_utilities_test_init`, `semanage_utilities_test_cleanup`, and `semanage_utilities_add_tests(CU_pSuite suite)`.

## Control Flow
The header contains declarations only.

## State and Persistence Behavior
It owns no state. Temporary-file setup and cleanup are implemented in `test_utilities.c`.

## Dependencies and Integration Points
The header intentionally has no include guard in the visible file, but its declarations are small and include CUnit for `CU_pSuite`. It connects the utilities suite to the test runner.

## Risks and Test Signals
Lack of an include guard could cause duplicate declarations if included repeatedly in unusual ways, though identical function declarations are generally harmless in C. Runtime signals are produced by `test_utilities.c`.
