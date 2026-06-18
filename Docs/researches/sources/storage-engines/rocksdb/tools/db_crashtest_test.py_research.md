<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest_test.py -->
# sources/storage-engines/rocksdb/tools/db_crashtest_test.py

## Purpose
This Python unit test file validates selected behavior in `db_crashtest.py` without running `db_stress`. It focuses on import safety, environment handling, parameter sanitization, SIGTERM stderr filtering, out-of-space detection, directory usage diagnostics, and multi-DB flag compatibility.

## Important APIs, Types, and Functions
- `load_db_crashtest_module()` imports `db_crashtest.py` under the synthetic module name `db_crashtest_under_test` while temporarily replacing `sys.argv` with only the script path. This isolates import-time argparse and random seeding.
- `DBCrashTestTest.setUp()` creates a temporary `TEST_TMPDIR`, clears `TEST_TMPDIR_EXPECTED`, and records old environment values.
- `tearDown()` restores `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, and `TSAN_OPTIONS`, then deletes the temp tree.
- `build_params()` copies a parameter map, injects the temp DB path, and applies test-specific overrides.

## Control Flow
Each test imports a fresh copy of `db_crashtest.py`, calls one helper or sanitizer, and asserts exact outputs. Environment-sensitive tests control `TSAN_OPTIONS` and temp-directory variables before import. Sanitization tests build representative parameter maps and verify only the relevant incompatible flags change. Diagnostic tests create a small filesystem tree, synthesize no-space stderr, and assert that generated diagnostic text contains aggregate and per-directory suffix summaries.

## State and Persistence Behavior
The test owns all filesystem state under a per-test temp directory. It explicitly checks that `get_ev_parent_dir()` does not remove existing expected-value contents. Out-of-space diagnostics create small marker files such as `CURRENT`, `.sst.trash`, and `.sst` to validate byte and suffix reporting. No RocksDB database is opened and no `db_stress` subprocess is started.

## Dependencies and Integration Points
The suite uses `unittest`, `importlib.util`, `tempfile`, `shutil`, and environment variables. It integrates directly with `db_crashtest.py` internals instead of a public CLI, so it is sensitive to function names and import-time side effects. The tests are designed to be run from the `tools` directory or any context where the relative `db_crashtest.py` path resolves.

## Risks and Edge Cases
- Since `db_crashtest.py` runs early parsing during import, test isolation depends on the temporary `sys.argv` replacement.
- These tests cover targeted invariants, not the full sanitizer matrix. Large portions of option interactions remain validated only by integration crash tests.
- Exact diagnostic string assertions can become brittle if formatting changes.
- Environment restoration in `tearDown()` is essential because TSAN and temp-dir variables influence later tests in the same process.

## Test Signals
The tests assert that default TSAN suppressions are added only when appropriate, expected-value directories are preserved, WAL-disabled and blob-direct-write modes disable batch/snapshot testing, range tombstone conversion disables SQFC range queries, SIGTERM stderr filtering hides only known retryable post-termination messages, no-space messages are detected, suffix extraction preserves compound suffixes, multi-DB mode disables unsupported operations, and diagnostics summarize local file usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest_test.py -->
