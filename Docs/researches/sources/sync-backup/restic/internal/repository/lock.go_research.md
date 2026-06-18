
# sources/sync-backup/restic/internal/repository/lock.go

Purpose: provides the high-level repository lock lifecycle, including acquisition retries, periodic refresh, stale-refresh recovery, and removal of stale or all locks. Public entry points are `LockRepo`, `RemoveStaleLocks`, and `RemoveAllLocks`; `Unlocker` is the user-facing interface.

Control flow in `locker.Lock` repeatedly calls `newLock`, handles `alreadyLockedError` with exponential backoff up to `retryLock`, wraps invalid locks into a fatal unlock hint, and returns a child context that is cancelled on unlock or failed refresh. Two goroutines manage lock health: `refreshLocks` periodically replaces the lock file and removes the old one; `monitorLockRefresh` uses wall-clock Unix time so host sleep does not hide refresh expiry. If a refresh becomes stale, `tryRefreshStaleLock` freezes freeze-capable backends while attempting safe replacement.

State is persisted in lock files via `lockHandle` from `lock_file.go`; this file owns runtime state, cancellation, and wait groups. Risks include goroutine coordination, wall-clock drift, backend latency during refresh, and correctly cancelling the caller before further repository mutations when lock refresh cannot be trusted. Tests in `lock_test.go` cover cancellation, conflicts, failed refresh, slow stale refresh recovery, retry timeout/cancel/success, stale-lock deletion, and force unlock.
