# sources/storage-engines/sqlite/src/mutex_noop.c

Purpose: implements SQLite's no-op mutex method table for single-threaded or platform-other builds where the mutex subsystem remains configurable but the default implementation provides no mutual exclusion. Debug builds add call-sequence checking without real locking.

Important APIs and types: `sqlite3NoopMutex()` returns the method table. Under `SQLITE_MUTEX_NOOP`, `sqlite3DefaultMutex()` aliases the no-op implementation. In debug builds, `sqlite3_debug_mutex` tracks mutex `id` and entry `cnt`; in non-debug builds, allocation returns the dummy pointer `(sqlite3_mutex*)8`.

Control flow: non-debug methods all succeed and ignore their arguments. Debug allocation returns heap objects for `SQLITE_MUTEX_FAST` and `SQLITE_MUTEX_RECURSIVE`, or entries from a static array for static mutex IDs. Debug enter/try assert that non-recursive mutexes are not already held, increment `cnt`, and always succeed. Debug leave asserts held state, decrements `cnt`, and asserts non-recursive mutexes return to not-held.

State and persistence: non-debug mode has no meaningful state. Debug mode stores dynamic counters per mutex and static counters for static mutexes, but it still does not serialize threads.

Dependencies and integration points: used by `mutex.c` when `sqlite3GlobalConfig.bCoreMutex` is false or by default when `SQLITE_MUTEX_NOOP` is selected. It depends on SQLite allocation helpers, API armor checks for invalid static IDs, and debug assert conventions.

Risks: this implementation is unsafe for concurrent use; it is valid only when the caller has selected single-thread/no-core-mutex behavior or supplied external serialization. Debug checking can catch recursive misuse in one thread but cannot detect cross-thread races. Static mutex misuse under API armor reports `SQLITE_MISUSE_BKPT` instead of freeing.

Test signals: compile with and without `SQLITE_DEBUG`; verify dynamic no-op mutex allocation/free API behavior; assert double-enter on a FAST mutex fails in debug tests; verify recursive enter/leave counts; and run single-thread SQLite suites with `SQLITE_MUTEX_NOOP`.
