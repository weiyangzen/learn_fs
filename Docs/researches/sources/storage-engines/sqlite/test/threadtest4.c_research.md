## sources/storage-engines/sqlite/test/threadtest4.c

### Purpose
`threadtest4.c` stresses multiple threads accessing the same group of attached databases in shared-cache mode. It varies attach order per worker to expose lock-ordering, shared-cache, VACUUM, and cross-database transaction issues.

### Important APIs, types, and functions
`WorkerInfo` tracks thread identity, flags, main and worker connections, error counters, messages, pthread id, and a write mutex. Flags are `TT4_SERIALIZED`, `TT4_WAL`, and `TT4_TRACE`. Helpers include `safe_malloc()`, `worker_trace()`, `prep_sql()`, `run_sql()`, `worker_open_connection()`, `worker_close_connection()`, `worker_delete_all_content()`, `worker_add_content()`, `worker_error()`, and `worker_thread()`.

### Control flow
`main()` parses options and thread count, requires a threadsafe SQLite build, enables shared cache, initializes three database files with tables and indexes, then starts `N` workers. Each worker repeatedly opens the three files in a rotating order, attaches the other two databases, inserts rows into all three tables under a write mutex, validates counts, sometimes releases memory, performs rollback updates, may run `VACUUM`, executes a join query while yielding, deletes its rows, and closes.

### State and persistence behavior
The test creates `tt4-test1.db`, `tt4-test2.db`, and `tt4-test3.db`, with optional WAL mode on the first connection. Worker data is partitioned by `tid`, then deleted before the next outer iteration. Writes are serialized by `wrMutex`, while reads and connection/attach sequencing remain concurrent.

### Dependencies and integration points
The file depends on SQLite shared-cache support, pthreads, POSIX scheduling and unlink, and SQLite memory allocation. It can be built with thread sanitizers and run in `--multithread` or `--serialized` modes.

### Risks and test signals
Because many write operations are mutex-serialized, the test is targeted at shared-cache and attach interactions rather than unrestricted write races. `run_sql()` treats ten repeated busy/locked retries as deadlock and exits immediately. Signals are per-worker startup/finish lines, joined error/test counts, optional trace output, and final total errors.
