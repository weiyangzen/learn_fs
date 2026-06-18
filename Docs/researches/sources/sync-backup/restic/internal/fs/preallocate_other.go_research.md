# sources/sync-backup/restic/internal/fs/preallocate_other.go

Purpose: Fallback preallocation for non-Linux, non-Darwin platforms.

Important APIs: `PreallocateFile`.

Control flow and state: Calls `wr.Truncate(size)`. On Windows this maps to `SetEndOfFile`, which may allocate disk space.

Dependencies and integration: Keeps callers platform-neutral even where true preallocation is unavailable.

Risks: Truncate changes file length and may create sparse files rather than reserving real blocks depending on filesystem.

Test signals: `preallocate_test.go` validates size/block outcomes generically.
