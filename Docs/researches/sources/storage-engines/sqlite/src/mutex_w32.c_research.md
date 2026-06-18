# sources/storage-engines/sqlite/src/mutex_w32.c

Purpose: provides the Windows default mutex backend for threadsafe Win32 builds selected by `SQLITE_MUTEX_W32`.

Important types and APIs: `struct sqlite3_mutex` stores either a `CRITICAL_SECTION` for recursive mutexes or an `SRWLOCK` for non-recursive/static mutexes, plus an `id` and debug owner/ref/trace fields. `sqlite3DefaultMutex()` returns the method table. `sqlite3MemoryBarrier()` supplies the platform barrier, and `sqlite3_win32_sleep()` is used while another thread initializes static mutexes.

Control flow: `winMutexInit()` uses `InterlockedCompareExchange()` on `winMutex_lock` so one caller initializes the aligned static mutex array and others wait for `winMutex_isInit`. Static mutexes use SRW locks. `winMutexAlloc()` heap-allocates dynamic FAST or RECURSIVE mutexes, initializes SRW or critical section accordingly, or returns a static entry by ID. Enter/try/leave dispatch on `id`: recursive uses critical-section APIs, all others acquire/release exclusive SRW locks. `winMutexEnd()` resets initialization state.

State and persistence: process-global static mutexes live in `aWindowsMutex[12]`. `winMutex_lock` and `winMutex_isInit` protect backend initialization state. Debug builds track owning thread ID and recursion count for assertions and optional tracing through `OSTRACE`.

Dependencies and integration points: depends on Windows primitives via `os_win.h`, `os_common.h`, MSVC alignment support, SQLite allocation, API armor, and `MSVC_VERSION`. It integrates with the common mutex dispatcher through `sqlite3DefaultMutex()`.

Risks: `winMutexEnd()` assumes shutdown ordering; resetting `winMutex_isInit` while mutex users remain would violate assertions. SRW locks are exclusive-only here and non-recursive, so accidental reentry into FAST/static mutexes is invalid. `TryAcquireSRWLockExclusive()` availability follows supported Windows targets. Static array bounds must track SQLite static mutex IDs.

Test signals: run Windows serialized-mode concurrency tests; build debug with dynamic/static mutex tracing; verify recursive critical-section reentry and FAST non-reentry assertions; test initialization races by parallel `sqlite3_initialize()` calls; and compile with MSVC and MinGW paths.
