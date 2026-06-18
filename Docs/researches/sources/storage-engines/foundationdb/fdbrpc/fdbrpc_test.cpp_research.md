# sources/storage-engines/foundationdb/fdbrpc/fdbrpc_test.cpp

## Purpose
`fdbrpc_test.cpp` is the main function for the fdbrpc unit-test executable.

## Important APIs, Types, and Functions
It defines `initializeSimulation()` and `main`. It uses `FDB_BOOLEAN_PARAM` declarations for `IsSimulated` and `Randomize`, `resetFlowKnobs`, `startUnitTestSimulator`, and `runUnitTests`.

## Control Flow
`main` calls `runUnitTests` with a `UnitTestRunnerConfig` named `fdbrpc` and an initialization function. Initialization resets Flow knobs for randomized simulation and starts the unit-test simulator.

## State and Persistence Behavior
It mutates global Flow knobs and starts simulator state for the process. It does not persist data directly.

## Dependencies and Integration Points
It depends on `fdbrpc/simulator.h`, `flow/Knobs.h`, `flow/UnitTestRunner.h`, and boolean parameter helpers. It is the executable entry point for the `TEST_CASE` definitions in fdbrpc sources.

## Risks and Edge Cases
All tests launched through this binary run under simulated/randomized knobs, so tests requiring real networking or non-simulated behavior need explicit guards. Initialization failure blocks the entire suite.

## Test Signals
The process exit code from `runUnitTests` is the primary signal. Individual fdbrpc `TEST_CASE` functions register into this runner.
