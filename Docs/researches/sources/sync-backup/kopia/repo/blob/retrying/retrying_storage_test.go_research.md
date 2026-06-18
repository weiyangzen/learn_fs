# sources/sync-backup/kopia/repo/blob/retrying/retrying_storage_test.go

Purpose: validates retry wrapper behavior.

Important APIs/types/functions: `TestRetrying`, `retrying.NewWrapper`, and a test storage that injects errors before success or permanent errors.

Control flow: the test configures operations to fail transiently and then succeed, ensuring the wrapper retries and returns success. It also exercises permanent errors that should not be retried according to `isRetriable`.

State and persistence behavior: state is in test counters and buffers. The test confirms output buffers are reset between read attempts.

Dependencies/integration points: validates integration with `internal/retry` and blob error sentinels. Risks/test gaps include no timing/backoff assertion, no context cancellation coverage, and no list/capacity retries because the wrapper does not implement those. The test is still important because cloud providers rely on this wrapper for transient resilience.
