# sources/security-integrity/selinux/libsemanage/tests/test_port.h

## Purpose
`test_port.h` declares the lifecycle hooks for the libsemanage port CUnit suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `port_test_init`, `port_test_cleanup`, and `port_add_tests(CU_pSuite suite)`.

## Control Flow
The header contains declarations only. The test runner calls these functions to set up a policy fixture, register tests, and clean up after execution.

## State and Persistence Behavior
The header has no state. File-backed test-store state is managed by `test_port.c` and shared utilities.

## Dependencies and Integration Points
The include guard is `__TEST_PORT_H__`; integration is with the central CUnit registry.

## Risks and Test Signals
The header must stay synchronized with `test_port.c`. Runtime validation signals are emitted by the implementation suite.
