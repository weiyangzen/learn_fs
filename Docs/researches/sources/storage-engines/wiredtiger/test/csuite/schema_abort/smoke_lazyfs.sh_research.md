# sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke_lazyfs.sh

Purpose: this smoke wrapper runs the schema abort crash-recovery harness with LazyFS enabled. LazyFS coverage is separated from the main smoke matrix because the storage-cache clearing behavior requires a longer timeout and different environmental assumptions.

Important APIs and variables: it uses POSIX `sh`, `set -e`, an optional first argument for the test binary, `binary_dir` fallback, and `TEST_WRAPPER`. The resolved binary defaults to `test_schema_abort`.

Control flow: after resolving the binary, it executes two runs: `-l -t 20 -T 5` and `-l -C -t 20 -T 5`. Both enable LazyFS explicitly, use five worker threads, and allow twenty seconds. The second run adds compatibility mode.

State and persistence behavior: persistent state is created by the underlying C test. LazyFS causes the child/parent flow to simulate filesystem cache loss and cleanup via `testutil_lazyfs_setup`, `testutil_lazyfs_clear_cache`, and `testutil_lazyfs_cleanup`.

Dependencies and integration points: the script depends on a build where LazyFS support is available or implicitly configured. It relies on `TEST_WRAPPER` for environment handling and on the same binary-location convention as the main schema abort smoke test.

Risks and test signals: the smoke signal is binary exit status. The matrix is small, so it checks LazyFS plus compatibility only, not the full row/column/timestamp/transaction cross product.
