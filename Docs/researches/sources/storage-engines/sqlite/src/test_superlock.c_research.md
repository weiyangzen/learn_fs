<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_superlock.c -->
# sources/storage-engines/sqlite/src/test_superlock.c

## Purpose
`test_superlock.c` is example and test code for obtaining a strong exclusive lock on a SQLite database in both rollback and WAL journal modes. It exposes `sqlite3demo_superlock()` and `sqlite3demo_superunlock()` plus Tcl bindings for testfixture.

## Important APIs, Types, And Functions
`Superlock` stores the locking database handle and WAL-mode flag. `SuperlockBusy` wraps a busy callback and counts invocations. Important functions are `superlockIsWal()`, `superlockShmLock()`, `superlockWalLock()`, `sqlite3demo_superlock()`, and `sqlite3demo_superunlock()`. Tcl commands are created by `SqliteSuperlock_Init()`.

## Control Flow
`sqlite3demo_superlock()` opens the target database, installs a wrapped busy handler, and executes `BEGIN EXCLUSIVE`. For rollback mode that is sufficient. For WAL mode it detects journal mode, commits the exclusive transaction to drop SQLite's own WAL locks, obtains the recovery shared-memory lock, zeroes the start of the first shared-memory page to force future clients into recovery, then locks all read-lock slots exclusively. Unlocking reverses the WAL shared-memory locks if needed and closes the private database handle.

## State And Persistence Behavior
The active lock is process state held by the private `sqlite3` connection and WAL shared-memory locks. In WAL mode the code intentionally writes zeros into the first shared-memory page, a transient coordination area, not the database file itself. The opaque lock handle must be released through `sqlite3demo_superunlock()`.

## Dependencies And Integration Points
It depends on SQLite busy-handler, open, exec, file-control, and VFS shared-memory methods. The Tcl wrapper creates a command whose deletion releases the lock and can call a Tcl busy script.

## Risks And Test Signals
Risks include VFSes lacking shared-memory support, stale or incompatible WAL lock constants, effects of zeroing shared memory on concurrent clients, and cleanup paths calling unlock on partially acquired locks. Test signals include blocking other readers/writers/checkpointers while locked, busy-handler count continuity across SQL and WAL-lock phases, successful rollback-mode locking with only `BEGIN EXCLUSIVE`, command deletion releasing locks, and clean error returns on busy or unsupported VFS paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_superlock.c -->
