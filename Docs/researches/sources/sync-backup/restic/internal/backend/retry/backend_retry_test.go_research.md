<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go -->
# sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go

## Purpose
Extensively tests retry wrapper behavior for save, list, load, stat, remove, permanent errors, callbacks, and context cancellation.

## Important APIs, Types, And Functions
Tests include SaveRetry, SaveRetryAtomic, List retry/dedup/error paths, failing readers, permanent error handling, success reporting, and circuit breaker behavior.

## Control Flow
Mock backends inject transient/permanent errors and track calls while fastRetries shortens backoff. Tests assert data rewind, cleanup removal rules, callback precedence, and retry counts.

## State And Persistence Behavior
No repository persistence; state is mock callbacks, buffers, and retry wrapper maps.

## Dependencies And Integration Points
Depends on mock backend, backoff, internal/errors/restic/test, context, io, time.

## Risks And Edge Cases
Because it toggles package-level fastRetries and feature behavior, isolation is important. It targets control semantics rather than real backend I/O.

## Test Signals
This is the primary regression suite for retry correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go -->
