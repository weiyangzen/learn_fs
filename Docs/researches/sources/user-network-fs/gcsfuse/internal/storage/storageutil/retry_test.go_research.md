## sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry_test.go

Purpose: Unit tests for retry backoff and generic retry executor behavior.

Important APIs/types/functions: suites `ExponentialBackoffTestSuite`, `RetryConfigTestSuite`, and `ExecuteWithRetryTestSuite`; tests cover `newExponentialBackoff`, `nextDuration`, `waitWithJitter`, `NewRetryConfig`, `ExecuteWithRetry`, and custom retry variants.

Control flow: backoff tests use small durations and assert growth/caps; executor tests use mock API functions returning success, retryable gRPC errors, non-retryable errors, context timeouts, and custom errors.

State and persistence behavior: temporarily redirects logger output for log verification. Tests rely on wall-clock timers but do not write persistent files.

Dependencies and integration points: validates compatibility with gRPC `codes.Unavailable`, context cancellation/deadline propagation, and internal logger levels.

Risks: timing thresholds may be flaky on overloaded systems. The suite does not seed or control jitter randomness, only bounds elapsed time.

Test signals: broad coverage of retry control-flow edges including parent context pre-cancel, shorter/longer deadline interactions, max attempts, total budget exhaustion, and log diagnostics.
