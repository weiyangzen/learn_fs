# sources/sync-backup/restic/internal/backend/cache/dir_test.go

Purpose: Tests cache directory environment override.

Important APIs and functions: `TestCacheDirEnv` validates `DefaultDir` when `RESTIC_CACHE_DIR` is set or temporarily set by the test.

Control flow and state: The test preserves/restores environment when it has to set the variable, then asserts the returned directory equals the environment value and no error occurs.

Dependencies and integration: Uses `os` environment APIs and `internal/test` assertions.

Risks and test signals: Guards user-configured cache location behavior across platforms.
