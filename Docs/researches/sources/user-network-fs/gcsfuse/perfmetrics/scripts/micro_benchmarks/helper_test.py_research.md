<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py

## Purpose
Unit tests for microbenchmark helper functions.

## Important APIs, Types, And Functions
Uses `unittest.mock.patch` and `MagicMock` to validate subprocess and BigQuery interactions.

## Control Flow
Tests call helper functions under mocked success and failure conditions, then assert boolean returns or propagated exceptions.

## State And Persistence Behavior
No persistent state; directory creation, subprocesses, and BigQuery load jobs are mocked.

## Dependencies
Depends on `helper`, `subprocess`, and stdlib unittest mocks.

## Integration Points
Confirms the helper contract consumed by read/write benchmark scripts.

## Risks And Edge Cases
Does not cover SQL query construction, alert exit behavior, or actual pandas-to-BigQuery schema compatibility.

## Test Signals
Covers mount/unmount success and failure plus BigQuery load success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py -->
