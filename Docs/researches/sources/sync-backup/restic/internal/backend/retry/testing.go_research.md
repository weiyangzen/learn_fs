<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/testing.go -->
# sources/sync-backup/restic/internal/backend/retry/testing.go

## Purpose
Provides a test helper to enable fast retry timing.

## Important APIs, Types, And Functions
TestFastRetries sets the package-level fastRetries flag.

## Control Flow
Calling the helper makes retry backoff millisecond-scale for tests.

## State And Persistence Behavior
Mutates package global test state only.

## Dependencies And Integration Points
Depends on testing.

## Risks And Edge Cases
Global mutation can affect other retry tests in the same package, which is intentional for speed.

## Test Signals
Used by backend_retry_test.go.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/testing.go -->
