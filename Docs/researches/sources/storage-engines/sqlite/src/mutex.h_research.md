# sources/storage-engines/sqlite/src/mutex.h

Purpose: selects the mutex implementation at compile time and defines mutex omission macros for `SQLITE_THREADSAFE=0` builds. It is included indirectly through `sqliteInt.h`.

Important macros: `SQLITE_MUTEX_OMIT` is defined when SQLite is not threadsafe. For threadsafe builds without explicit `SQLITE_MUTEX_NOOP`, the header selects `SQLITE_MUTEX_PTHREADS` on Unix, `SQLITE_MUTEX_W32` on Windows, or `SQLITE_MUTEX_NOOP` for other platforms. When mutexes are omitted, public mutex operations become macros that return a dummy `(sqlite3_mutex*)8`, no-op enter/leave/free, successful try, and true held/notheld checks. `MUTEX_LOGIC(X)` either erases or preserves mutex-only declarations and code.

Control flow: the file has no runtime control flow. Its preprocessor decisions decide which `.c` backend compiles and whether common code emits mutex logic.

State and persistence: no runtime state. The dummy pointer used by omit-mode macros is never dereferenced and exists only to satisfy API shape.

Dependencies and integration points: depends on `SQLITE_THREADSAFE` and OS macros from `os_setup.h` via `os.h`. It declares `sqlite3_mutex_held()` when real mutexes are present. Many core modules use `MUTEX_LOGIC()` and `sqlite3MutexAlloc()` behavior chosen here.

Risks: platform macro misclassification routes builds to the wrong backend or to no-op mutexes. In omit mode, mutex logic is compiled away completely and cannot be replaced at start time, unlike `SQLITE_MUTEX_NOOP`. Code added to the core must respect `MUTEX_LOGIC()` or null/dummy mutex behavior.

Test signals: compile with `SQLITE_THREADSAFE=0`, `SQLITE_THREADSAFE=1` on Unix and Windows, explicit `SQLITE_MUTEX_NOOP`, and `SQLITE_OS_OTHER`; verify only the expected backend symbols are required; and run API tests for mutex calls under omit and no-op modes.
