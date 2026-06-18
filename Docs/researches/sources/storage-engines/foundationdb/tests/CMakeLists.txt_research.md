<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CMakeLists.txt -->
# Research: sources/storage-engines/foundationdb/tests/CMakeLists.txt

## Purpose
Central CMake registry and configuration for FoundationDB correctness, simulation, restart, unit, status, multiversion-client, and packaging-related tests.

## Important APIs, Types, And Functions
Defines cache options such as `ENABLE_BUGGIFY`, `ENABLE_SIMULATION_TESTS`, `RUN_IGNORED_TESTS`, log retention controls, include/exclude regexes; finds an old fdbserver for restart tests; configures the Python test runner; calls `configure_testing`, many `add_fdb_test` entries, `verify_testing`, package creation helpers, and optional unit-test discovery.

## Control Flow
When Python is available, it configures test metadata, computes ignore patterns based on multiregion/restart/RocksDB/UBSAN/Valgrind options, registers fast/slow/rare/negative/status/restarting tests, and adds direct CTest unit commands. If Python is absent it warns and skips CTest setup. At the end, optional `AUTO_DISCOVER_UNIT_TESTS` collects unit tests.

## State And Persistence Behavior
Writes configured test runner files into the build tree, registers CTest targets, and controls generated correctness packages. Test execution later writes logs/sim dirs according to cache options.

## Dependencies And Integration Points
Depends on local CMake modules (`AddFdbTest`), Python, built `fdbserver`, many `.toml`/`.txt` tests, optional RocksDB/multiregion/restart build flags, and package helper macros. This file is the main integration point between FoundationDB simulation workloads and CTest/CI.

## Risks And Edge Cases
Large manually maintained test list can drift from filesystem contents; `configure_testing(... ERROR_ON_ADDITIONAL_FILES)` mitigates that. Many tests are explicitly ignored pending fixes or environment needs. Old-fdbserver fallback to current binary weakens upgrade coverage.

## Test Signals
The file itself defines the test signal: registered CTest names, ignored markers, restart sequences, RocksDB-gated tests, direct unit filters, and verification via `verify_testing`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CMakeLists.txt -->
