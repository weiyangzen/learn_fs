## sources/storage-engines/sqlite/test/tt3_stress.c

### Purpose
`tt3_stress.c` contributes two broad shared-cache stress tests to `threadtest3`. `stress1` mixes schema creation/drop, reads, inserts, deletes, and connection churn. `stress2` runs a larger set of concurrent workload classes including DDL, DML, VACUUM, integrity checks, journal-mode switching, and rapid open/close.

### Important APIs, types, and functions
`stress_thread_1()` through `_5()` implement `stress1` worker classes. `stress2_workload1()` through `_17()` implement individual workload functions, while `stress2_workload19()` handles connection churn. `Stress2Ctx`, `stress2_thread_wrapper()`, and `stress2_launch_thread_loop()` adapt workload functions to threadtest3 threads.

### Control flow
`stress1` sets the stop time, enables shared cache, launches two table create/drop workers, two schema scan workers, two table read workers, two insert workers, and two delete workers, then joins all threads. `stress2` initializes `t0` and index `i0`, enables shared cache, launches one thread per workload function plus two connection-churn threads, then joins them.

### State and persistence behavior
Both tests use `test.db`. `stress1` intentionally makes table `t1` appear and disappear, so many `SQLITE_LOCKED` and `SQLITE_ERROR` results are expected and cleared. `stress2` keeps base table `t0` but creates and drops side tables, changes journal mode, vacuums, and mutates rows concurrently.

### Dependencies and integration points
The file relies on `threadtest3` wrappers, shared-cache mode, SQLite recursive CTE support for bulk inserts, VACUUM, `PRAGMA integrity_check`, and journal-mode transitions.

### Risks and test signals
The stress tests intentionally tolerate several concurrency errors, so the risk is clearing too broad a class of failures. There is also a small leak of `Stress2Ctx` allocations because thread return cleanup does not free the context. Signals are per-thread attempt summaries, no unhandled errors after expected clears, and the final threadtest3 global error count.
