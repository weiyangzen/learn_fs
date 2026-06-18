# sources/storage-engines/sqlite/test/wordcount.c

## Purpose
`wordcount.c` is a standalone benchmark and behavior test utility that tokenizes alphabetic words from an input stream and applies one of several SQLite update strategies to a `wordcount(word TEXT PRIMARY KEY, cnt INTEGER)` table. It compares insert/update, replace, upsert, select/update, delete, and query paths, optionally across rowid and `WITHOUT ROWID` table layouts.

## Important APIs, Types, and Functions
The program uses the public SQLite C API: `sqlite3_open()`, `sqlite3_exec()`, `sqlite3_prepare_v2()`, `sqlite3_bind_text()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_db_status()`, `sqlite3_status()`, and `sqlite3_create_function()`. `realTime()` uses the active VFS clock. `checksumStep()` and `checksumFinalize()` implement a small aggregate used by summary queries. `allLoop()` drives `--all` mode across all operation modes and both table layouts.

## Control Flow
`main()` parses options, deletes the target database unless it is empty or `:memory:`, opens the database and input file, configures pragmas, and enters the selected mode loop. Each loop creates the table inside `BEGIN IMMEDIATE`, prepares the SQL statements needed by that mode, reads lines into a fixed buffer, extracts alphabetic spans, binds each word using `SQLITE_STATIC` while the line buffer is still valid, and executes the appropriate statement sequence. It commits periodically if `--commit` is set, finalizes statements, then optionally prints query totals, timing, summary SQL, and memory/cache statistics.

## State and Persistence
The main persistent state is the target SQLite database and its `wordcount` table. The program unlinks an existing non-memory database at startup, except repeated `--all` iterations reuse the same connection and drop/vacuum the table between iterations. Options such as page size, cache size, journal mode, synchronous mode, collation, and `WITHOUT ROWID` affect database state when the table/database is newly created. `sumCnt`, timers, counters, and prepared statements are process-local.

## Dependencies and Integration Points
The file depends on `sqlite3.h`, the C runtime, and `unistd.h` or `io.h` for unlink behavior. It is integrated into SQLite testing and benchmarking as a command-line utility compiled with `sqlite3.c`. Its SQL mode variants exercise conflict handling, primary key updates, statement preparation, transaction behavior, status counters, and aggregate function registration.

## Risks
Input lines longer than 1999 bytes are processed in chunks, so words split across buffer boundaries are not treated as one word. `SQLITE_STATIC` bindings are safe only because statements are stepped and reset before the input buffer changes. `--all` requires a seekable input file and explicitly rejects stdin. The utility intentionally deletes the output database at startup, which is correct for benchmarks but destructive if used carelessly. Error handling exits immediately and may leave a partially processed database if failures occur mid-run.

## Test Signals
Useful signals include identical summaries across `--insert`, `--replace`, `--upsert`, `--select`, and `--update`; expected destructive behavior for `--delete`; stable `checksum()` output for a fixed corpus; timing output under `--timer` and `--all`; `PRAGMA integrity_check` in summary mode; and memory/status counters returning low or zero outstanding allocations after close.
