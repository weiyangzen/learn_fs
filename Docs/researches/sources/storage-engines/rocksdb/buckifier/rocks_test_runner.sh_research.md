# sources/storage-engines/rocksdb/buckifier/rocks_test_runner.sh

## Purpose

`rocks_test_runner.sh` is a small Buck test wrapper that creates a temporary test directory under shared memory, runs the provided test command with `TEST_TMPDIR` set to that directory, and removes the directory on success.

## Control Flow

1. Create a temporary directory with `mktemp -d /dev/shm/fbcode_rocksdb_XXXXXXX`.
2. Execute all script arguments as the test command with `TEST_TMPDIR="$TEST_DIR"` in the command environment.
3. If the command succeeds, remove the temporary directory with `rm -rf "$TEST_DIR"`.

The script includes `# shellcheck disable=SC2068` because it intentionally expands `$@` unquoted. That preserves the legacy invocation style but has argument-splitting implications.

## State and Persistence Behavior

The script persists only a temporary directory in `/dev/shm`. Cleanup happens only after successful test execution because the command is chained with `&& rm -rf "$TEST_DIR"`. If the test command fails, crashes, or is interrupted, the temp directory remains for post-failure inspection or later cleanup.

`TEST_TMPDIR` is scoped to the invoked command only; it is not exported for later shell commands except through that environment assignment.

## Dependencies and Integration Points

- Requires `/dev/shm` to exist and allow temporary directory creation.
- Requires `mktemp`.
- Expects callers to pass the actual test command and arguments.
- Integrates with RocksDB tests that honor `TEST_TMPDIR` for temporary database/test files.
- Likely used by generated Buck test rules or macros in the buckifier template stack.

## Risks and Edge Cases

- Unquoted `$@` can split arguments containing spaces or glob characters. This may be intentional for Buck command construction but is fragile for arbitrary commands.
- No `trap` is installed, so interrupts and failures leave the `/dev/shm/fbcode_rocksdb_*` directory behind.
- Cleanup only on success means repeated failing tests can accumulate shared-memory usage.
- If `/dev/shm` is unavailable or too small, the wrapper fails before running the test.
- The script does not propagate cleanup diagnostics; failures are dominated by the test command or `mktemp`.

## Test Signals

Useful validation signals:

- Running `rocks_test_runner.sh true` should create and then remove a temp directory and exit `0`.
- Running it with a failing command should exit nonzero and leave the directory for inspection.
- Tests that rely on RocksDB temp directories should see `TEST_TMPDIR` set to a `/dev/shm/fbcode_rocksdb_*` path.
