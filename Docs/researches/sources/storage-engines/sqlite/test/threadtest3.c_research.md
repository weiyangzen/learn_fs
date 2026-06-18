## sources/storage-engines/sqlite/test/threadtest3.c

### Purpose
`threadtest3.c` is the main modern multithreaded SQLite stress-test harness. It contains common infrastructure and several built-in tests, then includes scenario files `tt3_*.c` to form one executable with glob-selectable tests for WAL, shared-cache, schema churn, checkpointing, vacuum, lookaside, and stress workloads.

### Important APIs, types, and functions
The harness defines `Error`, `Sqlite`, `Statement`, `Thread`, and `Threadset`. Macros such as `opendb`, `sql_script`, `execsql_i64`, `launch_thread`, and `setstoptime` record source lines before delegating to `_x` implementations. It embeds an MD5 aggregate (`md5step()`, `md5finalize()`), statement caching (`getSqlStatement()`), SQL execution helpers, cross-platform thread launch/join, file-size/copy helpers, and a VFS-backed timer. Built-in tests include `walthread1` through `walthread5`, `cgt_pager_1`, and `dynamic_triggers`.

### Control flow
`main()` configures SQLite multithread mode, parses `-multiplexor` and test glob arguments, validates that each argument matches at least one test, then runs matching entries from `aTest`. Each test initializes `test.db`, sets a stop time, launches workers, joins them, prints thread results, and increments the global error count through `print_err()`.

### State and persistence behavior
Most tests use `test.db` plus WAL, journal, or saved copies. Connections cache prepared statements and stored text results until `closedb_x()`. WAL tests intentionally exercise checkpoint behavior, journal-mode transitions, snapshot isolation, and file replacement. The harness treats some transient `SQLITE_SCHEMA`, `SQLITE_LOCKED`, and missing-table errors as warnings or clearable expected concurrency effects.

### Dependencies and integration points
It depends on SQLite public APIs, pthreads or Windows threads, `test_multiplex.h`, optional multiplex VFS initialization, and included `tt3_*.c` files. The include pattern means the scenario files rely on symbols from this harness rather than compiling independently.

### Risks and test signals
Risks include global `timelimit` shared by all threads, expected lock/schema errors hiding unexpected failures if clear rules are too broad, and workload sensitivity to filesystem timing. Strong signals are the final `N errors out of M tests`, per-thread summaries, integrity checks, MD5 consistency checks, WAL size assertions, and nonzero exit status on global errors.
