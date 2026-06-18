
# sources/sync-backup/restic/internal/repository/lock_file.go

Purpose: implements the persisted lock-file format and low-level locking algorithm. `Lock` is JSON-serialized with timestamp, exclusivity flag, host/user/process identifiers, and optional UID/GID. `lockHandle` binds a `Lock` to the repository and current lock ID.

Important APIs include `newLock`, `LoadLock`, `IsAlreadyLocked`, `TestSetLockTimeout`, `unlock`, `refresh`, `refreshStaleLock`, `stale`, and `forAllLocks`. `newLock` checks for conflicts, writes a lock file using `restic.SaveJSONUnpacked`, waits for backend consistency, then checks again. Non-exclusive locks can coexist; exclusive locks conflict with any other valid lock. `forAllLocks` lists locks in parallel but serializes callbacks and ignores zero-length lock files left by non-atomic uploads.

State transitions are create-lock, optionally replace-lock-on-refresh, adopt replacement by updating `lockID`, then remove old lock with a delayed cancellation context. Stale detection uses age, host equality, and platform-specific process liveness. Risks include unreadable locks being treated as blocking, delayed lock visibility on eventual-consistency backends, and safe cleanup if replacement creation succeeds but old-lock verification fails. Tests in `lock_file_test.go` exercise mutual exclusion, invalid/unreadable locks, stale decisions, refresh, and missing stale refresh cases.
