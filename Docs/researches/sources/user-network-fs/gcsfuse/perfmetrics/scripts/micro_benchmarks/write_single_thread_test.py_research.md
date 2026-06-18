<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py

## Purpose
Unit tests for write microbenchmark filesystem helpers.

## Important APIs, Types, And Functions
Imports `create_files`, `delete_existing_file`, and `write_random_file` directly and patches `os.path.exists`, `os.remove`, `open`, and `os.urandom`.

## Control Flow
Tests validate existing-file deletion, missing-file no-op, write success/failure, aggregate size calculation, and SystemExit on create failure.

## State And Persistence Behavior
No durable state because all local IO is mocked.

## Dependencies
Depends on local `write_single_thread` and stdlib unittest mocks.

## Integration Points
Protects the write helper contract used by the CLI and periodic wrapper.

## Risks And Edge Cases
Does not cover mount/unmount, BigQuery logging, threshold check, or the real memory behavior of large `os.urandom` calls.

## Test Signals
Focused helper coverage with mocked IO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py -->
