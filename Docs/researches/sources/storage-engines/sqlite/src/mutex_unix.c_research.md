# sources/storage-engines/sqlite/src/mutex_unix.c

Purpose: provides the pthread-based default mutex backend for threadsafe Unix builds selected by `SQLITE_MUTEX_PTHREADS`.

Important types and APIs: `struct sqlite3_mutex` wraps a `pthread_mutex_t` plus optional `id`, `nRef`, `owner`, and `trace` fields when debug, API armor, or homegrown recursive mutex support needs them. The exported backend hook is `sqlite3DefaultMutex()`, and the file also defines `sqlite3MemoryBarrier()`.

Control flow: `pthreadMutexAlloc()` returns heap mutexes for `SQLITE_MUTEX_RECURSIVE` and `SQLITE_MUTEX_FAST`, and static cache-line-aligned mutexes for IDs 2 through 13. Recursive mutexes use `PTHREAD_MUTEX_RECURSIVE` unless `SQLITE_HOMEGROWN_RECURSIVE_MUTEX` is defined, in which case owner/nRef emulate recursion on a normal pthread mutex. `pthreadMutexEnter()`, `pthreadMutexTry()`, and `pthreadMutexLeave()` update owner/nRef fields when enabled and delegate to pthread lock primitives. `pthreadMutexFree()` destroys and frees only dynamic mutexes.

State and persistence: static mutexes live for process lifetime in `aMutex[]`; dynamic mutexes are heap allocated. Debug/homegrown builds track owner and recursion count for assertions and recursive behavior. There is no persistent storage.

Dependencies and integration points: depends on `<pthread.h>`, SQLite allocation helpers, API armor, debug asserts, and `GCC_VERSION` for alignment and memory barrier selection. `sqlite3MemoryBarrier()` uses `SQLITE_MEMORY_BARRIER` or GCC `__sync_synchronize()` and is consumed by the mutex dispatch and VFS shared-memory barriers.

Risks: held/notheld checks rely on `pthread_equal()` behaving atomically enough for debug assertions; comments call out HPUX-style risk. Homegrown recursive mutexes assume coherent cache and safe owner comparison. Static mutex array size must match SQLite static mutex IDs. If `pthread_mutexattr_settype(PTHREAD_MUTEX_RECURSIVE)` is unavailable or fails silently, recursive behavior can break.

Test signals: run threaded SQLite tests on Unix with serialized mode; run debug builds to exercise owner/nRef assertions; compile with `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`; verify static mutex IDs under API armor; and run stress tests for recursive db mutex use and `sqlite3_mutex_try()` contention.
