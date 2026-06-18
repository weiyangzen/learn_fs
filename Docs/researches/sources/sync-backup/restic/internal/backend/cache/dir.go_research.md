# sources/sync-backup/restic/internal/backend/cache/dir.go

Purpose: Resolves the base cache directory.

Important APIs and functions: `EnvDir` returns `RESTIC_CACHE_DIR`. `DefaultDir` returns that env value when set, otherwise uses `os.UserCacheDir()` joined with `restic`.

Control flow and state: No persistent state is changed. Errors from `os.UserCacheDir` are wrapped with context.

Dependencies and integration: Used by `Cache.New` when no explicit base directory is provided. Depends on `os`, `filepath`, and `fmt`.

Risks and test signals: Platform-specific user cache lookup can fail. `dir_test.go` verifies environment override behavior.
