
# sources/sync-backup/restic/internal/repository/lock_test.go

Purpose: validates the high-level lock supervisor in `lock.go`, including acquisition, context cancellation, retry behavior, refresh failure, slow backend recovery, stale lock deletion, and force unlock.

Important helpers are `openLockTestRepo`, `checkedLockRepo`, `writeOnceBackend`, `loggingBackend`, `slowBackend`, `createFakeLock`, `lockExists`, and `removeLock`. Tests cover ordinary unlock cancellation, parent context cancellation, exclusive/non-exclusive conflicts, failed periodic refresh cancelling the wrapped context, successful refresh under normal and stale timing, wait timeout/cancel/success semantics, removal of stale locks, and removal of all locks.

State and persistence checks use actual lock files in an in-memory backend, often reopening a repository to simulate multiple clients. The tests intentionally shorten refresh intervals and timeouts to make goroutine behavior observable. Risks covered include backend write failure after initial lock creation, refresh blocked longer than the safe timeout, retry backoff respecting cancellation, and ensuring fresh current-process locks are not removed as stale. These tests are strong integration signals for lock safety during long-running commands.
