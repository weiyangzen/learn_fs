<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml

## Purpose
TOML workload definition for running performance unit tests through the FoundationDB test runner.

## Important APIs, Types, And Functions
Defines one `[[test]]` named `PerfUnitTests`, `useDB = false`, no start delay, and a `UnitTests` workload with `testsMatching = #`.

## Control Flow
The test runner reads this file and runs a unit-test workload without starting/using a database.

## State And Persistence Behavior
No persistent state aside from normal test output/logs.

## Dependencies And Integration Points
Depends on FoundationDB test runner TOML schema and `UnitTests` workload implementation. Registered by `tests/CMakeLists.txt` as an ignored test file.

## Risks And Edge Cases
The broad `testsMatching = #` selector relies on workload interpretation. Being marked ignored means it will not run unless ignored tests are enabled.

## Test Signals
Test signal is explicit but disabled by default via `IGNORE` in CMake.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/PerfUnitTests.toml -->
