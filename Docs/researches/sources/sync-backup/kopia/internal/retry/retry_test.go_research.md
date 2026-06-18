# sources/sync-backup/kopia/internal/retry/retry_test.go

Purpose: tests retry helper behavior.

Important APIs/types/functions: `TestRetry`, `TestRetryContextCancel`, sentinel `errRetriable`, and `isRetriable`.

Control flow: uses attempts that fail then succeed or remain failing, asserts number of calls and returned errors, and cancels context to ensure retry exits.

State and persistence behavior: no persistence; counters are local to tests.

Dependencies and integration points: validates public retry functions in-package to access helpers.

Risks and test signals: tests should stay fast despite sleeps; fake clock or short intervals are important for deterministic CI.
