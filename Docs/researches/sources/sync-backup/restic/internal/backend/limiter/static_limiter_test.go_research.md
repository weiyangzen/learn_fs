<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go -->
# sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go

## Purpose
Tests static limiter wrappers for non-nil wrapping, actual read/write delay, HTTP body wrapping, close propagation, and corner cases.

## Important APIs, Types, And Functions
TestLimiterWrapping, TestReadLimiter, TestWriteLimiter, TestRoundTripperReader, TestRoundTripperCornerCases, and tracedReadCloser are key.

## Control Flow
Tests read/write known byte counts through low KB/s limits and assert elapsed time exceeds a minimum. RoundTripper tests inject response bodies and inspect wrapper behavior.

## State And Persistence Behavior
No persistent state; timing is wall-clock based and in-memory.

## Dependencies And Integration Points
Depends on bytes, io, net/http, testing, time, and package limiter.

## Risks And Edge Cases
Timing assertions can be noisy on overloaded hosts; tests choose coarse thresholds to reduce flakes.

## Test Signals
Provides direct unit coverage for limiter correctness and body close behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go -->
