# sources/storage-engines/sqlite/src/threads.c

## Purpose

`threads.c` is SQLite's small internal worker-thread abstraction. It supports real pthread worker threads on Unix, real `_beginthreadex()` worker threads on native Windows, and a deterministic single-thread fallback. The abstraction is compiled only when `SQLITE_MAX_WORKER_THREADS>0` and is used by SQLite features that can optionally parallelize work without requiring an application to use a threaded build path.

## Important APIs, Types, And Functions

- `SQLiteThread` is backend-specific. Pthread builds store `pthread_t`, completion flag, result, task function, and input. Win32 builds store thread handle, id, task function, input, and result. Fallback builds store task function/input or immediate result.
- `sqlite3ThreadCreate(SQLiteThread **, void *(*)(void*), void*)` starts or schedules a worker task and always returns an allocated `SQLiteThread` on success.
- `sqlite3ThreadJoin(SQLiteThread *, void **ppOut)` joins or executes the task and frees the `SQLiteThread`.
- `sqlite3FaultSim(200)` forces deterministic sequential execution in pthread and Win32 backends for test control.
- Win32 builds call `sqlite3Win32Wait(HANDLE)` from `os_win.c` before closing the thread handle.

## Control Flow

When pthread support is available, `sqlite3ThreadCreate()` allocates state, records the task, and either starts `pthread_create()` or, if fault simulation/thread creation fails, executes the task synchronously and marks it done. Join returns the synchronous result directly or calls `pthread_join()`.

On Windows, creation allocates state and uses `_beginthreadex()` unless core mutexes are disabled or fault simulation requests deterministic execution. Failed or disabled thread creation falls back to immediate execution on the caller thread. The thread entry shim stores `xTask(pIn)` in `pResult` and calls `_endthreadex()`. Join waits with `sqlite3Win32Wait()`, closes the handle, returns `pResult` on `WAIT_OBJECT_0`, and frees the wrapper.

If no real backend is compiled, creation randomly chooses based on the allocated pointer value whether to defer work until join or run it immediately. Join runs deferred work if needed, includes a small `SQLITE_TEST` allocation probe, frees the wrapper, and returns `SQLITE_OK`.

## State And Persistence Behavior

All state is transient heap state owned by `SQLiteThread` and freed by join. Worker results are opaque pointers returned through `ppOut`; SQLite callers own any result payload. The module does not persist database state by itself, but worker tasks may read or produce data for higher-level SQLite operations.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, SQLite memory allocation, fault simulation, compile-time OS/thread macros, pthreads, `os_win.h`, `_beginthreadex()`, and `sqlite3Win32Wait()`. It is an internal abstraction consumed by SQLite worker-thread users and honors `sqlite3GlobalConfig.bCoreMutex` to avoid real threading when core mutexing is disabled.

## Risks And Edge Cases

- `sqlite3ThreadCreate()` can execute the task before returning; callers must not assume asynchronous execution.
- Join is mandatory to retrieve results and free `SQLiteThread`.
- Pthread creation failure is not surfaced as an error; it silently falls back to synchronous execution.
- Win32 join treats non-`WAIT_OBJECT_0` as `SQLITE_ERROR` and then frees wrapper state; callers must handle missing output.
- The fallback backend's pointer-value choice intentionally varies execution timing, so tests should not rely on a fixed create-vs-join execution point unless fault simulation or compile options force it.
- Task functions must be valid until execution, including fallback deferred execution.

## Test Signals

Tests should cover real backend success, forced synchronous mode via `sqlite3FaultSim(200)`, join result propagation, create-time allocation failure, task execution exactly once, Win32 wait/close behavior, pthread join errors if injectable, and single-thread fallback immediate/deferred paths.
