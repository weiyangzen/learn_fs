# sources/sync-backup/restic/internal/backend/cache/cache_test.go

Purpose: Tests cache directory initialization and repair.

Important APIs and functions: `TestNew` exercises `New` with a random repository ID and a temporary base directory.

Control flow and state: The test creates a cache, then removes `CACHEDIR.TAG` and `version` in later iterations. Each call to `New` must recreate missing files, preserve the base path, and report `Created` only for the first creation step.

Dependencies and integration: Uses `restic.NewRandomID`, `internal/test`, `os`, and `filepath`.

Risks and test signals: Guards startup behavior when users delete metadata files or re-open an existing cache. It does not cover newer-version rejection or old-cache listing.
