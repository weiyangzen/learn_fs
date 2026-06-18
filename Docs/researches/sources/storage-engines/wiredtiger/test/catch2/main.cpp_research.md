# sources/storage-engines/wiredtiger/test/catch2/main.cpp

## Purpose
Provides the Catch2 test runner entry point for the WiredTiger Catch2 suite and cleans the default test home before running tests.

## Important APIs, Types, And Functions
Defines `CATCH_CONFIG_RUNNER`, includes Catch2, includes `utils.h`, and implements `main` by calling `utils::wiredtiger_cleanup(DB_HOME)` before `Catch::Session().run(argc, argv)`.

## Control Flow
Startup removes leftovers from previous crashed or failed runs, then delegates argument parsing and test execution to Catch2.

## State And Persistence Behavior
The only persistent side effect is cleanup of `DB_HOME`. It does not create connections itself.

## Dependencies And Integration Points
Integrates Catch2's custom runner mode with WiredTiger test utility cleanup.

## Risks And Edge Cases
Shared `DB_HOME` cleanup is useful but can remove state a developer expected to inspect after a failed test if rerun immediately.

## Test Signals
The process exit code is Catch2's run result after cleanup succeeds.
