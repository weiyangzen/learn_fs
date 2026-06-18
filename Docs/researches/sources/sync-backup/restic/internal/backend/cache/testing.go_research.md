# sources/sync-backup/restic/internal/backend/cache/testing.go

Purpose: Shared cache test helper for constructing isolated cache instances.

Important APIs and constants: `testCacheID` is a stable 64-character hex ID. `TestNewCache` creates a temporary directory and calls `New` with that ID.

Control flow and state: Each call creates a new temp base directory, logs it, initializes the cache, and fails the test on error.

Dependencies and integration: Uses `internal/test.TempDir` and the package's `New` function. It is consumed by cache backend and file tests.

Risks and test signals: The helper reduces duplicated setup but hardcodes a single ID; tests that need multiple cache IDs must not reuse it blindly.
