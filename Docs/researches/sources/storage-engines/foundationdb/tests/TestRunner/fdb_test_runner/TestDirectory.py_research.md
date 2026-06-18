<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py

## Purpose
Utility script for creating and locating timestamped FoundationDB test run directories in a build tree.

## Important APIs, Types, And Functions
`TestDirectory.get_test_root` creates `<builddir>/test_runs`, `create_new_test_dir` creates a timestamped subdirectory, `get_current_test_dir` returns the lexicographically latest run directory, and `main` parses `builddir` and creates a new directory.

## Control Flow
When run, it ensures the root exists then creates a directory named with current date/time down to microseconds.

## State And Persistence Behavior
Persists directories under the supplied build directory. It does not write files beyond directory creation.

## Dependencies And Integration Points
Depends on Python stdlib `os`, `datetime`, and `argparse`. Used by `CTestCustom.ctest.cmake` before CTest runs.

## Risks And Edge Cases
`get_current_test_dir` assumes at least one run directory exists and will fail on empty roots. Concurrent invocations could collide only at microsecond-level timestamp names, but no retry exists.

## Test Signals
Validated by CTest pre-test invocation; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestDirectory.py -->
