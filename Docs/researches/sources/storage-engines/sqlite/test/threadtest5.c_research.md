## sources/storage-engines/sqlite/test/threadtest5.c

### Purpose
`threadtest5.c` tests many connections in separate pthreads working against the same database file or URI database. It implements a simple task queue where workers claim tasks atomically, build two prime-number tables by different methods, and verify that the final sets match.

### Important APIs, types, and functions
Global state includes `zDbName` and `eVerbose`. `error_out()` aborts on non-OK setup errors, `exec()` and `prepare()` wrap formatted SQL execution and preparation, `waitOnTable()` polls `sqlite_schema`, `isPrime()` filters prime candidates, `worker()` claims and runs tasks, and `usage()` documents options.

### Control flow
`main()` parses a database name, `-num-workers`, and `-v`, defaults to `file:/mem?vfs=memdb`, enables URI handling, creates a `task` table with 100 tasks, launches workers, and joins them. Workers use `UPDATE ... RETURNING` to claim one unassigned task. Task 1 creates `p1`; tasks 2-51 insert prime numbers into `p1`; task 52 creates `p2` containing 1..10000; tasks 53-62 delete composites from `p2`. The main thread prints task ownership and verifies `p1` and `p2` are equal with `EXCEPT` queries.

### State and persistence behavior
The default database is an in-memory memdb URI shared by connections. A supplied database path persists until overwritten by setup drops. Task claims are stored in `task.doneby`, and final computed state lives in `p1` and `p2`.

### Dependencies and integration points
The program depends on SQLite URI support, pthreads, `sqlite3_sleep()`, `UPDATE RETURNING`, and the memdb VFS for the default mode. It is Unix-oriented and standalone.

### Risks and test signals
`isPrime()` returns true for values below 2, so `p2` intentionally retains `1` to match `p1` semantics if generated; this is a test convention, not mathematical primality. Busy handling is a fixed 2 second timeout. Signals are successful task ownership output, `OK`, no incorrect-result messages, and no abort from prepare/open/exec wrappers.
