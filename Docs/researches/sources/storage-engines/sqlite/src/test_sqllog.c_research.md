<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_sqllog.c -->
# sources/storage-engines/sqlite/src/test_sqllog.c

## Purpose
`test_sqllog.c` implements an experimental `SQLITE_CONFIG_SQLLOG` callback that captures initial database contents and expanded SQL statements from live applications for offline analysis, replay, and performance investigation.

## Important APIs, Types, And Functions
State is stored in `SLConn` per logged connection and singleton `SLGlobal`. `sqlite3_init_sqllog()` installs the callback when `SQLITE_SQLLOG_DIR` is set. Core helpers include `sqllogOpenlog()`, `sqllogCopydb()`, `sqllogFindAttached()`, `sqllogFindFile()`, `testSqllogStmt()`, `sqllogTraceDb()`, and callback `testSqllog()`. Environment variables are `SQLITE_SQLLOG_DIR`, `SQLITE_SQLLOG_REUSE_FILES`, and `SQLITE_SQLLOG_CONDITIONAL`.

## Control Flow
On connection open, the callback lazily initializes global mutex state, optionally checks for a sibling `-sqllog` trigger file, allocates an `SLConn`, opens a per-connection SQL log, and backs up the main database into the log directory. On statement completion, non-`ATTACH` SQL is written with a clock comment; `ATTACH` causes the newly attached database to be copied and an `ATTACH '<copy>' AS '<name>'` statement to be logged. On close, the connection log is closed and the array compacted.

## State And Persistence Behavior
The module persists `sqllog_<pid>_<n>.sql`, database copy files, and an index file mapping database-copy ids to original paths. Global counters allocate log names and logical clock values. `bRec` suppresses recursive logging while PRAGMA and backup operations run. Reuse mode avoids duplicate database copies by consulting the index.

## Dependencies And Integration Points
It depends on `SQLITE_ENABLE_SQLLOG`, environment variables, SQLite backup APIs, mutexes, `sqlite3_log()`, stdio, process id lookup, and filesystem access checks. It integrates before or during SQLite initialization through `sqlite3_config(SQLITE_CONFIG_SQLLOG, ...)`.

## Risks And Test Signals
Risks include fixed path buffers, `MAX_CONNECTIONS` bounds without graceful expansion, best-effort error handling, reliance on expanded SQL text, conditional logging path assumptions, and replay differences for application-defined functions or external side effects. Test signals include creation of SQL, DB, and index files; correct handling of repeated opens with and without reuse; `ATTACH` capture; no recursive self-logging; close cleanup; and logged errors rather than crashes when output files fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_sqllog.c -->
