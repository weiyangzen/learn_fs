# sources/sync-backup/kopia/repo/maintenance/blob_retain.go

Purpose: extends object-lock retention on repository blobs when the blob backend supports retention.

Important APIs/types/functions: `ExtendBlobRetentionTimeOptions`, `extendBlobRetentionTime`, `CheckExtendRetention`, `parallelBlobRetainCPUMultiplier`, and `minRetentionMaintenanceDiff`.

Control flow: the task loads blob retention config, exits with nil stats when retention is disabled, starts worker goroutines, iterates all locking-storage prefixes in parallel, sends blob metadata to workers, and calls `ExtendBlobRetention` with repository retention mode/period. It records counts and fails if any extension failed.

State/persistence behavior: mutates backend blob retention metadata, not repository content. It uses content logs and returns `ExtendBlobRetentionStats`.

Dependencies/integration: depends on `repo.GetLockingStoragePrefixes`, blob storage retention APIs, `format.BlobStorageConfiguration`, content logging, and maintenance stats.

Risks/test signals: a broad prefix set could extend unrelated blobs; worker errors are counted and converted to a task error. `CheckExtendRetention` guards against full maintenance intervals too close to retention expiry. Tests cover enabled and disabled retention behavior.
