## sources/storage-engines/sqlite/test/tt3_vacuum.c

### Purpose
`tt3_vacuum.c` adds `vacuum1`, a shared-cache test that runs VACUUM concurrently with write-heavy table activity.

### Important APIs, types, and functions
`vacuum1_thread_writer()` repeatedly inserts 100 blob rows, deletes by rowid, and selects rows ordered by primary key, clearing expected `SQLITE_LOCKED`. `vacuum1_thread_vacuumer()` repeatedly runs `VACUUM`, also clearing `SQLITE_LOCKED`. `vacuum1()` initializes the table and index, enables shared cache, launches three writers and one vacuumer, then joins all threads.

### Control flow
The setup creates `t1(x PRIMARY KEY, y BLOB)` plus an index on `y`. Writers and the vacuumer run until the shared stop time expires. The test then disables shared cache and reports accumulated errors.

### State and persistence behavior
The test mutates `test.db` heavily, growing and compacting it while multiple connections are active. Inserts are durable unless interrupted by lock errors; deletes and selects are part of the stress loop. VACUUM rewrites the database file when it can obtain the required locks.

### Dependencies and integration points
This file depends on `threadtest3` infrastructure, SQLite shared-cache mode, VACUUM behavior, and lock handling across concurrent connections.

### Risks and test signals
Expected lock contention is cleared, so meaningful failures are unhandled SQLite errors, corruption, crashes, or global error count increments. Useful signals are `ok` summaries from all four workers and no final errors.
