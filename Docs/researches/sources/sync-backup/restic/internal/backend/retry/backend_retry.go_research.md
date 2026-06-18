<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry.go -->
# sources/sync-backup/restic/internal/backend/retry/backend_retry.go

## Purpose
Decorates a backend with retry, backoff, success/failure reporting, upload rewind, list de-duplication, and optional failed-load circuit breaking.

## Important APIs, Types, And Functions
Backend, New, retryNotifyErrorWithSuccess, retryAtLeastOnce, retry, Save, Load, Stat, Remove, List, Unwrap, Warmup, and WarmupWait are important.

## Control Flow
retry creates exponential backoff with feature-flag-dependent settings, reports retries/final errors, treats permanent backend errors specially, and guarantees at least one attempt. Save rewinds before each attempt and removes partial files on non-atomic backends. Load records non-permanent exhausted failures in a one-hour circuit breaker. List suppresses duplicate callbacks across retries.

## State And Persistence Behavior
State includes MaxElapsedTime, callbacks, wrapped backend, and failedLoads sync.Map. Repository persistence is delegated.

## Dependencies And Integration Points
Depends on cenkalti/backoff, internal/backend/debug/feature, context, sync, time.

## Risks And Edge Cases
Risks include incorrectly classifying permanent errors, duplicate list callbacks, deleting partial files on non-atomic backends, circuit breaker false positives, and canceled-context modification guarantees.

## Test Signals
backend_retry_test.go provides extensive targeted coverage; testing.go speeds retry timing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry.go -->
