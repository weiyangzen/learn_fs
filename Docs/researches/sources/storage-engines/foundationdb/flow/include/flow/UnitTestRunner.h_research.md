# sources/storage-engines/foundationdb/flow/include/flow/UnitTestRunner.h

## Purpose
Declares the common runner interface for Flow unit-test binaries, including suite naming and optional simulation initialization.

## Important APIs, Types, And Functions
`UnitTestRunnerConfig` holds a source subdirectory and optional `SimulationInitializer`. It exposes `suiteName`, `dataDir`, `traceName`, `supportsSimulation`, and `initializeSimulation`. `runUnitTests` is the executable entry point.

## Control Flow
Unit-test mains construct a config and call `runUnitTests`. The implementation handles CLI parsing, trace/data directory setup, filtering, and simulation initialization when configured.

## State And Persistence Behavior
The config stores string-view/callback state. Runtime traces and test data directories are created by the implementation, not this header.

## Dependencies And Integration Points
Depends on `flow/flow.h` and standard function/string headers. Used by fdbserver and fdbclient unit-test main programs.

## Risks And Edge Cases
`sourceSubDir` is a `std::string_view`; callers must pass long-lived storage. Suites without an initializer must not claim simulation support.

## Test Signals
Suite naming, filtering, trace/data naming, simulation gating, and execution through representative test mains.
