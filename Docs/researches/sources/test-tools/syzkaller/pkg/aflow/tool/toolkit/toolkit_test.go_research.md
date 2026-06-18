# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit_test.go

## Purpose
Linux-only compile/run tests for C files under toolkit testdata.

## Important APIs, Types, and Functions
`TestToolkitsInTestData` discovers `testdata/*.c`, selects gcc or clang, compiles with `-I . -pthread`, and executes each binary.

## Control Flow
If no compiler exists the test skips. Each C file is compiled into a temp binary, then executed with combined output captured for failures/logging.

## State and Persistence Behavior
Creates temporary binaries only. No persistent state.

## Dependencies and Integration Points
Depends on host C compiler and Linux runtime support for the toolkit tests.

## Risks and Test Signals
Excellent signal for header compile health and functional primitives, but host privileges can affect userfaultfd and CPU affinity behavior.
