# sources/sync-backup/kopia/internal/retry/retry.go

Purpose: generic retry helpers for value-returning and no-value operations with exponential or fixed-interval backoff.

Important APIs/types/functions: `IsRetriableFunc`, `WithExponentialBackoff`, `WithExponentialBackoffMaxRetries`, `Periodically`, `PeriodicallyNoValue`, `WithExponentialBackoffNoValue`, `NoValueFn`, `Always`, `Never`, and `internalRetry`.

Control flow: `internalRetry` runs attempts until success, context cancellation, non-retriable error, or retry count exhaustion. Between failures it logs and sleeps interruptibly using a configurable interval, factor, and max sleep.

State and persistence behavior: stateless except for local counters and sleep duration.

Dependencies and integration points: shared by network/storage/repository operations that need retry policies.

Risks and test signals: off-by-one retry counts and context cancellation handling are critical. Tests cover success after retries, non-retriable stop, max retry exhaustion, and cancellation.
