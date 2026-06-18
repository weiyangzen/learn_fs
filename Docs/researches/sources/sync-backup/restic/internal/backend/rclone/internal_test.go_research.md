<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/internal_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/internal_test.go

## Purpose
Tests rclone subprocess failure and exit handling paths without running full backend suite.

## Important APIs, Types, And Functions
TestRcloneExit and TestRcloneFailedStart are key.

## Control Flow
The tests start commands that exit or fail and assert newBackend/Open reports useful errors and cleans up.

## State And Persistence Behavior
State is subprocess-local and temporary.

## Dependencies And Integration Points
Depends on package internals, context, exec-like behavior, and testing.

## Risks And Edge Cases
External shell/command behavior can vary by platform; tests target robust error propagation.

## Test Signals
Covers lifecycle paths that normal happy-path integration tests may miss.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/internal_test.go -->
