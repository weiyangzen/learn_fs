# sources/sync-backup/borg/src/borg/fslocking.py

Purpose: implements filesystem-based locking primitives used to coordinate shared and exclusive access across Borg processes and machines.

Important APIs and types: constants `ADD`, `REMOVE`, `REMOVE2`, `SHARED`, `EXCLUSIVE`; `TimeoutTimer` handles timeout/sleep loops; lock error classes expose specific exit codes; `ExclusiveLock` uses atomic directory replacement to acquire a lock and stores ownership as a file named from platform process identity; `LockRoster` stores shared/exclusive owners in JSON and removes stale owners; `Lock` composes an exclusive filesystem lock and roster to provide shared/exclusive resource locking, upgrade/downgrade, break, and ownership migration.

Control flow and state: `ExclusiveLock.acquire()` creates a temp dir and unique owner file, attempts to replace the target lock dir, kills stale locks when possible, and loops until success or timeout. `release()` verifies ownership and removes owner/dir. `Lock.acquire(exclusive=True)` waits for all shared readers to leave while holding the exclusive lock; shared acquire updates the roster under the exclusive lock. Roster state is persisted in `<path>.roster`, while the mutex directory is `<path>.exclusive`.

Dependencies and integration: uses `platform.get_process_id()` and `platform.process_alive()` for owner identity/staleness, Borg `Error` classes, JSON, temp dirs, `Path`, errno, and logging. Intended for repository/cache/resource locking layers.

Risks: lock correctness depends on filesystem atomic rename/replace semantics and reliable process liveness across hosts. Multiple shared lockers attempting `upgrade()` can deadlock, explicitly warned in code. `break_lock()` forcibly removes roster/lock files and must be administrative. Corrupt roster JSON is treated as empty, which favors recovery but can lose lock visibility.

Test signals: cover exclusive acquire/release/reentrant by-me behavior, timeout, stale lock killing and disabled stale killing, malformed lock names, shared lock coexistence, exclusive waiting for readers, upgrade/downgrade, roster corruption handling, ownership migration, break_lock, and cross-platform Windows permission retry behavior.
