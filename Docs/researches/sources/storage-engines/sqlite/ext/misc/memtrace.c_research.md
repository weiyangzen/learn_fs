# sources/storage-engines/sqlite/ext/misc/memtrace.c

Purpose: installs a process-global memory allocator tracing shim for SQLite, used by the shell `--memtrace` option.

Important APIs/types/functions: `memtraceBase` saves the original `sqlite3_mem_methods`; `memtraceOut` stores the log stream. `memtraceMalloc()`, `memtraceFree()`, `memtraceRealloc()`, `memtraceSize()`, `memtraceRoundup()`, `memtraceInit()`, and `memtraceShutdown()` wrap allocator methods. `sqlite3MemTraceActivate()` and `sqlite3MemTraceDeactivate()` install/restore the shim.

Control flow: activation fetches the current allocator with `SQLITE_CONFIG_GETMALLOC`, installs `ersaztMethods` with `SQLITE_CONFIG_MALLOC`, and records output. Each wrapper logs when enabled then delegates. Deactivation restores the original methods and clears globals.

State and persistence: global process state until deactivated; only diagnostic output is persisted externally.

Dependencies/integration: must be compiled into the application and activated before SQLite initialization for reliable `sqlite3_config()` behavior.

Risks/test signals: activation ordering, global thread visibility, output recursion, and restore correctness. Test pre-init activation, null stream, realloc/free edge cases, logging sizes, and deactivation restore.
