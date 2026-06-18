## sources/storage-engines/sqlite/test/startup.c

### Purpose
`startup.c` benchmarks SQLite startup costs, especially opening a database and parsing a large schema. The schema is modeled on Fossil repository, checkout, and global configuration databases, so it stresses schema loading, indexes, views, triggers, `WITHOUT ROWID` tables, and statistics tables without depending on row-level workload costs.

### Important APIs, types, and functions
The large `zTestSchema` string is the primary fixture. `usage()`, `hexDigitValue()`, and `integerValue()` support command-line processing. `displayLinuxIoStats()` reports `/proc/PID/io` counters on Linux. `main()` implements the `init` and `run` commands, optional `--dbname`, `--heap`, `--stats`, and `--autovacuum` parsing, though `bAutovac` is parsed but not used in the current logic.

### Control flow
`startup init` removes the database, journal, and WAL files, opens the database, runs `BEGIN`, executes `zTestSchema`, commits, and closes. `startup run` optionally configures a static heap before opening, opens the existing database, executes `PRAGMA synchronous` to force schema access, optionally prints database and global memory statistics, closes, and frees heap storage.

### State and persistence behavior
The persistent artifact is `startup.db` or the `--dbname` target. Initialization creates only schema objects, with no bulk data population. Run mode should be read-mostly, but opening the database may create transient journal/WAL artifacts depending on environment. Heap and memory statistics are process-local and printed after connection close.

### Dependencies and integration points
The file depends on `sqlite3.h`, POSIX `unlink()`, libc parsing and I/O, optional Linux `/proc`, and SQLite status APIs. It is intended for external profilers such as cachegrind, not for the Tcl test runner.

### Risks and test signals
The embedded schema contains compatibility-sensitive SQL and object names; changes to schema parsing or SQLite DDL behavior affect the benchmark. `run` prints SQLite errors but may continue to stats reporting, so exit status alone is a weak signal. Useful signals are absence of open/exec errors, stable schema heap and statement heap metrics, and Linux I/O counter deltas under profiling.
