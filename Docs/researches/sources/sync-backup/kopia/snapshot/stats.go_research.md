# sources/sync-backup/kopia/snapshot/stats.go

Purpose: defines snapshot generation counters and a helper for excluded entries.

Important APIs/types/functions: `Stats` and `AddExcluded`.

Control flow: `AddExcluded` checks `md.IsDir()`. Directories increment `ExcludedDirCount`; files increment `ExcludedFileCount` and add `md.Size()` to `ExcludedTotalFileSize` using atomic operations.

State and persistence: stats are in-memory counters intended for concurrent snapshot/upload/estimate progress reporting and JSON serialization. The struct arranges int64 and int32 fields for atomic updates.

Dependencies and integration points: used by upload estimation and snapshot generation to report included, cached, non-cached, excluded, ignored-error, and fatal-error counts.

Risks and test signals: only exclusion helper logic lives here; callers must atomically update other fields themselves. Directory sizes are not added to excluded total size. Tests assert file and directory exclusion effects exactly.
