# sources/storage-engines/sqlite/src/mutex.c

Purpose: provides the platform-independent mutex dispatch layer. It chooses the configured mutex implementation, initializes and tears it down, exposes the public `sqlite3_mutex_*` APIs, and optionally wraps the default implementation with contention warnings for misuse detection.

Important APIs and types: `sqlite3MutexInit()`, `sqlite3MutexEnd()`, `sqlite3_mutex_alloc()`, `sqlite3MutexAlloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, and debug-only `sqlite3_mutex_held()` / `sqlite3_mutex_notheld()`. Under `SQLITE_THREAD_MISUSE_WARNINGS`, `CheckMutex` wraps a real mutex and can mark recursive db-handle mutexes as `SQLITE_MUTEX_WARNONCONTENTION` through `sqlite3MutexWarnOnContention()`.

Control flow: `sqlite3MutexInit()` fills `sqlite3GlobalConfig.mutex` if the application did not configure one before initialization. It picks `sqlite3DefaultMutex()` when core mutexes are enabled, or `sqlite3NoopMutex()` when disabled, with an optional `multiThreadedCheckMutex()` wrapper. It copies method pointers, issues a memory barrier, then publishes `xMutexAlloc` last. Allocation uses `sqlite3_initialize()` for dynamic mutexes unless autoinit is omitted; static mutex allocation can call `sqlite3MutexInit()` directly. Runtime operations are thin null-tolerant dispatchers to the configured method table.

State and persistence: the global method table in `sqlite3GlobalConfig.mutex` is the central mutable state. Debug builds also maintain `mutexIsInit` to assert that internal mutex allocation occurs only after initialization. No persistent storage is involved.

Dependencies and integration points: platform backends provide `sqlite3DefaultMutex()` in `mutex_unix.c`, `mutex_w32.c`, or `mutex_noop.c`. The layer depends on `sqlite3GlobalConfig.bCoreMutex`, `sqlite3MemoryBarrier()`, `sqlite3_initialize()`, and SQLite's config-time mutex override API. Assertions and TSAN conditional logic protect debug-only held/notheld checks.

Risks: publishing method pointers out of order could allow another thread to see a partially initialized table, hence the barrier and last assignment to `xMutexAlloc`. Wrapper misuse warnings deliberately log `SQLITE_MISUSE` and may abort when configured. `sqlite3MutexAlloc()` returns null if core mutexes are disabled, so call sites must treat null as a valid no-op mutex.

Test signals: run single-thread, multithread, and serialized SQLite modes; configure custom mutex methods before initialization; enable `SQLITE_THREAD_MISUSE_WARNINGS` and verify contention logs; run debug assertions around static mutex allocation; and run under TSAN to confirm held/notheld checks are suppressed as intended.
