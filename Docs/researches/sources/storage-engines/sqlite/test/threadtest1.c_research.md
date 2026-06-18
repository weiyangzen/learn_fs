## sources/storage-engines/sqlite/test/threadtest1.c

### Purpose
`threadtest1.c` is an older standalone pthread program that probes SQLite thread safety by running pairs of threads against shared database files. Each thread repeatedly creates, populates, queries, validates, and drops its own table in a shared database.

### Important APIs, types, and functions
The program uses the legacy `sqlite.h` interface with `sqlite *`, `sqlite3_open()`, `sqlite3_exec()`, and `sqlite3_close()`. `db_is_locked()` is a busy handler with short sleeps. `QueryResult`, `db_query_callback()`, `db_query()`, `db_execute()`, `db_query_free()`, and `db_check()` form a small SQL execution and validation layer. `worker_bee()` is the thread body, and `main()` creates detached pthreads and waits on a condition variable.

### Control flow
`main()` accepts an optional thread count, deletes stale database files, creates thread arguments such as `1.testdb-1` and `2.testdb-1`, launches detached workers, and waits for `thread_cnt` to reach zero. Each worker opens the file named after the prefix, installs the busy handler, creates table `tN`, inserts 100 rows, checks count and average values, deletes half the rows, reads back each remaining row, drops the table, closes, and repeats ten times.

### State and persistence behavior
The test uses temporary database files named `testdb-N` and old rollback journals. It deletes files at start and end but leaves thread argument allocations unfreed. Per-thread SQL tables are transient. Validation state is held in heap-allocated query result arrays.

### Dependencies and integration points
It depends on pthreads, POSIX `unlink()` and `usleep()`, legacy SQLite headers, and SQLite formatting helpers. It sits outside the normal library and is useful for historical thread-safety regression testing.

### Risks and test signals
Because detached workers increment `thread_cnt` inside the thread, a very fast main thread can reach the wait before workers increment the count; in practice startup prints and scheduling usually hide this race. Busy handling is bounded, so lock pressure can become test failure. Signals are `START`/`END` messages, exact aggregate checks, readback checks, and process exit through `Exit(1)` on any SQL or validation error.
