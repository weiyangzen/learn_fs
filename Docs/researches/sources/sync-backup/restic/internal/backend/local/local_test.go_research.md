<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_test.go -->
# sources/sync-backup/restic/internal/backend/local/local_test.go

## Purpose
Runs the generic backend suite against the local backend and tests permission behavior.

## Important APIs, Types, And Functions
newTestSuite, TestBackendLocal, BenchmarkBackendLocal, and permission-related tests are the main items.

## Control Flow
The suite creates a temporary repo, runs standard save/load/list/stat/remove/delete behavior, and benchmarks common operations.

## State And Persistence Behavior
Uses real temporary directories and local filesystem metadata.

## Dependencies And Integration Points
Depends on backend/test Suite, local.NewFactory, and internal/test helpers.

## Risks And Edge Cases
Tests are sensitive to filesystem permission semantics; chmod behavior can vary on non-POSIX or special mounts.

## Test Signals
Broad integration signal for backend contract compliance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_test.go -->
