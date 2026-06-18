<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake -->
# Research: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake

## Purpose
CTest customization template that prepares a per-run test directory before tests execute.

## Important APIs, Types, And Functions
Sets `CTEST_CUSTOM_PRE_TEST` to invoke `TestDirectory.py` with the configured Python interpreter and project binary directory.

## Control Flow
CTest runs this command before tests, causing a timestamped directory to be created under the build tree.

## State And Persistence Behavior
Persists build-tree `test_runs/<timestamp>` directories.

## Dependencies And Integration Points
Depends on Python and `tests/TestRunner/fdb_test_runner/TestDirectory.py`. Configured by `tests/CMakeLists.txt` into the build tree.

## Risks And Edge Cases
If the pre-test command fails, test execution setup can fail broadly. It assumes the build directory is writable.

## Test Signals
Validated whenever CTest starts a configured test run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/CTestCustom.ctest.cmake -->
