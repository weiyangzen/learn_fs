# sources/storage-engines/foundationdb/flow/FlowTest.cpp

## Purpose
Defines the `flow` unit-test executable entry point.

## Important APIs, Types, And Functions
`main(int argc, char** argv)` calls `runUnitTests(argc, argv, UnitTestRunnerConfig("flow"))`.

## Control Flow
Process startup delegates immediately to the common Flow unit-test runner configured for the `flow` suite, and returns its exit code.

## State And Persistence Behavior
No local state. Test runner behavior may initialize global Flow state, run registered tests, and emit logs.

## Dependencies And Integration Points
Depends on `flow/UnitTestRunner.h`. It links together test cases registered across Flow source files.

## Risks And Edge Cases
Any missing force-link symbol or build target omission can cause tests in other translation units not to register. The entry point itself is intentionally minimal.

## Test Signals
Successful execution of the `flow` test binary is the direct signal.
