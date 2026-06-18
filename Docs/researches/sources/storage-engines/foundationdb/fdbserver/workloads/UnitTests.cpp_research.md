# sources/storage-engines/foundationdb/fdbserver/workloads/UnitTests.cpp

## Purpose
`UnitTestWorkload` bridges Flow/FoundationDB `TEST_CASE` unit tests into the simulation workload runner. It discovers linked unit tests, filters and randomizes them, executes them, collects timing/failure metrics, and optionally cleans per-test data directories.

## Important APIs, Types, and Functions
The source declares many `forceLink...Tests()` functions to keep unit-test translation units from being dead-stripped. `UnitTestWorkload` uses `g_unittests`, `UnitTest`, `UnitTestParameters`, `PerfIntCounter`, `PerfDoubleCounter`, `platform::eraseDirectoryRecursive()`, and `platform::createDirectory()`. It also defines `TEST_CASE("/fdbserver/UnitTestWorkload/long delay")`.

## Control Flow
The constructor reads filtering options, ignored patterns, max test count, data directory, cleanup flag, consumes remaining options into `testParams`, and calls all force-link functions. `setup()` erases the data directory. Client 0 `start()` runs `runUnitTests()`: collect tests whose names match the prefix and do not match ignore prefixes, sort them for stable discovery, fail if none match, shuffle deterministically, apply a run limit, then execute each test while timing wall and Flow time. Per-test data directories are created before execution and optionally erased after.

## State and Persistence Behavior
Persistent filesystem state is the unit-test data directory, defaulting to `simfdb/unittests/` in simulation and `unittests/` otherwise. The workload erases this directory during setup and optionally after each test. Database state is not directly used by this wrapper, although individual unit tests may use their data directory or other services.

## Dependencies and Integration Points
It integrates with Flow's unit test registry, many force-linked test modules, tester workloads, platform filesystem helpers, deterministic random ordering, stdout, and trace logging. GRPC tests are linked only when `FLOW_GRPC_ENABLED` is defined.

## Risks and Edge Cases
The workload treats no matching tests as a test failure. Remaining workload options are passed as string test parameters, so option-name collisions can affect unit tests. Running tests in randomized order may expose shared global state between unit tests. Long-running tests can extend simulation time, as shown by the embedded long-delay test.

## Test Signals
Metrics include test cases available, executed, failed, total wall time, and total flow time. Traces include `NoMatchingUnitTests`, `RunningUnitTest`, and `UnitTest` with result status. `check()` succeeds only when `testsFailed == 0`.
