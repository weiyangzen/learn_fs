# sources/security-integrity/selinux/libsemanage/tests/test_node.h

## Purpose
`test_node.h` exposes the CUnit lifecycle functions for the libsemanage node test suite.

## Important APIs, Types, and Functions
The header includes `<CUnit/Basic.h>` and declares `node_test_init`, `node_test_cleanup`, and `node_add_tests(CU_pSuite suite)`.

## Control Flow
There is no logic in this header; it provides declarations consumed by the central test runner.

## State and Persistence Behavior
State is created, mutated, and cleaned up in `test_node.c` and the shared test utilities. The header does not own state.

## Dependencies and Integration Points
Its include guard is `__TEST_NODE_H__`. It integrates `test_node.c` with the CUnit suite registry.

## Risks and Test Signals
Compile-time consistency with the implementation and runner is the relevant signal for this file. Runtime behavior is validated by the `test_node.c` suite.
