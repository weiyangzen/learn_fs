
# sources/sync-backup/restic/internal/repository/lock_file_test.go

Purpose: tests the low-level lock-file implementation independent of the high-level locker refresh supervisor. It creates in-memory test repositories, shortens lock timing with `TestSetLockTimeout`, and validates lock-file creation, conflict behavior, stale handling, and refresh behavior.

Important test cases include `TestLockFile`, `TestDoubleUnlock`, `TestMultipleLock`, `TestMultipleLockFailure`, `TestLockExclusive`, `TestLockOnExclusiveLockedRepo`, `TestExclusiveLockOnLockedRepo`, `TestLockStale`, `TestLockRefresh`, `TestLockRefreshStale`, and `TestLockRefreshStaleMissing`. The helper `failLockLoadingBackend` forces lock loads to fail to verify unreadable lock files prevent unsafe acquisition. `checkSingleLock` confirms only one lock remains after refresh.

State and persistence checks are direct: tests list lock files, remove locks, mutate timestamps and PIDs, and validate that stale replacement removes the old ID only when the old lock still exists. Risks covered include double unlock erroring, non-exclusive coexistence, exclusive exclusion, stale process recognition, invalid lock load handling, and cleanup after failed stale refresh. The suite is an important signal for eventual-consistency lock semantics.
