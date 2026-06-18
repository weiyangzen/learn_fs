## sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry.go

Purpose: Implements generic retry execution with per-attempt deadlines, total retry budget, max attempts, jittered exponential backoff, logging, and custom retry predicates.

Important APIs/types/functions: constants `DefaultRetryDeadline`, `DefaultTotalRetryBudget`, `DefaultInitialBackoff`; `exponentialBackoffConfig`, `exponentialBackoff`; `RetryConfig`; `NewRetryConfig`; `ExecuteWithCustomShouldRetryAtLogLevel`, `ExecuteWithCustomShouldRetry`, `ExecuteWithRetryAtLogLevel`, and `ExecuteWithRetry`.

Control flow: executor checks pre-cancelled context, wraps parent with total budget, then loops attempts with per-attempt timeout. It logs initial call at caller-supplied level and retries at warning, stops on success, max attempts, non-retryable error, parent timeout, or backoff cancellation.

State and persistence behavior: no persistent state. Backoff state is per operation. Uses package-global `math/rand` for jitter and internal logger.

Dependencies and integration points: used by auth universe-domain lookup and storage retry wrappers. Coupled to `StorageClientConfig` retry fields and `ShouldRetryWithoutLogging`.

Risks: random jitter and real timers make tests timing-sensitive. If retry predicate is too broad, errors can be retried until budget exhaustion. Error wrapping mixes last server/client error with context errors; callers should use `errors.Is` for context.

Test signals: `retry_test.go` covers backoff growth, jitter bounds, cancellation, retry config construction, success/failure paths, parent versus total deadlines, max attempts, custom predicates, and retry log content.
