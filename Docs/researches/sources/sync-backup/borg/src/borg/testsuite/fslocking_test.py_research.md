# sources/sync-backup/borg/src/borg/testsuite/fslocking_test.py

Purpose: validates Borg filesystem lock primitives: timeout timers, exclusive directory locks, shared/exclusive roster locks, stale lock cleanup, lock migration after daemonization, and roster persistence.

Important APIs and control flow: `free_pid` finds a likely unused local PID using `get_process_id` and `process_alive`. `TestTimeoutTimer` verifies timeout and sleep pacing. `TestExclusiveLock` covers context manager acquisition, break/reacquire, timeout when owned, killing stale local locks, refusing unknown remote-host locks, lock ID migration, and a Windows-skipped 40-thread race loop that asserts no concurrent exclusive holders. `TestLock` covers shared coexistence, exclusive acquisition, upgrade/downgrade idempotence, exclusive-state queries, break, timeout matrix, stale cleanup, and migration for both modes. `TestLockRoster` verifies serialized roster load/save, add/remove semantics, stale local lock pruning while keeping unknown remote locks, and roster ID migration.

State and persistence: writes lock files and roster files under pytest temporary directories. State is keyed by `(host, pid, tid)` identity and is intentionally sensitive to whether a PID is live on the local host.

Dependencies and integration points: depends on `borg.fslocking` (`TimeoutTimer`, `ExclusiveLock`, `Lock`, `LockRoster`, constants, exceptions), platform PID helpers, threading, and `is_win32`. Repository and cache code rely on these locks for concurrency safety.

Risks: free-PID selection is inherently racy. The threaded race test is timing-sensitive and skipped on Windows. Remote-host stale locks cannot be proven dead and therefore intentionally block acquisition.

Test signals: expected timeout/exception behavior, roster contents, lock ownership checks, successful migration, and no concurrent exclusive holders in the stress test.
