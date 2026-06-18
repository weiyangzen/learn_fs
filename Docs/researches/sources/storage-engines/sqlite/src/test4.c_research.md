<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test4.c -->
# sources/storage-engines/sqlite/src/test4.c

## Purpose
`test4.c` provides a Unix pthread-based Tcl harness for multithreaded SQLite tests. It allows Tcl scripts to create named worker threads, issue prepare/step/finalize operations, inspect row results and errors, swap or transfer SQLite handles, and halt threads.

## Important APIs, Types, and Functions
The `Thread` structure stores leader-written command fields (`zFilename`, `xOp`, `zArg`, `opnum`, `busy`) and worker-written result fields (`completed`, `db`, `pStmt`, `zErr`, `rc`, `argc`, `argv`, `colv`). `threadset[26]` maps IDs `A` through `Z`. Registered commands include `thread_create`, `thread_wait`, `thread_halt`, `thread_argc`, `thread_argv`, `thread_colname`, `thread_result`, `thread_error`, `thread_compile`, `thread_step`, `thread_finalize`, `thread_swap`, `thread_db_get`, `thread_db_put`, and `thread_stmt_get`.

## Control Flow
`thread_create` initializes a slot and launches a detached pthread running `test_thread_main()`. The worker opens the database, reports initial completion, then spins until the leader increments `opnum`. Each requested operation is a function pointer (`do_compile`, `do_step`, or `do_finalize`) executed in the worker thread. `test_thread_wait()` uses a static SQLite app mutex as a memory barrier and busy-waits until `completed` catches up. Halt sets `xOp` to null, advances `opnum`, waits for final cleanup, and releases stored strings.

## State and Persistence Behavior
Each thread owns an SQLite connection and optionally a prepared statement. Step results hold pointers returned by SQLite column APIs; they remain valid only while the statement remains positioned and unfinalized. `thread_db_get()` and `thread_stmt_get()` remove ownership from the worker and return pointer strings to Tcl, while `thread_db_put()` injects a pointer back into a worker slot. `thread_swap()` exchanges live `sqlite3*` handles between two idle worker threads.

## Dependencies and Integration Points
The file compiles only when `SQLITE_OS_UNIX && SQLITE_THREADSAFE`. It uses pthreads, `sched_yield()`, Tcl command APIs, `sqlite3_open()`, `sqlite3_prepare()`, `sqlite3_step()`, `sqlite3_finalize()`, `sqlite3_close()`, `sqlite3_thread_cleanup()` when not omitted, `sqlite3ErrName()`, and pointer-string helpers from the test harness.

## Risks
The synchronization model is intentionally primitive: shared fields are ordinary memory plus busy waiting and app-mutex barriers, not condition variables. Detached threads mean lifecycle mistakes can leak or race. Result column pointers are not copied. Pointer transfer commands can move database and statement ownership across threads in ways that would be unsafe outside misuse tests. `zErr` ownership is mixed between heap strings and static strings and depends on `zStaticErr`.

## Test Signals
Tests observe per-thread `SQLITE_*` result names, error text, column count, column values, and column names. Important coverage includes concurrent open/prepare/step/finalize behavior, handle handoff between worker and main thread, swapped connections, and clean shutdown of all busy slots with `thread_halt *`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test4.c -->
