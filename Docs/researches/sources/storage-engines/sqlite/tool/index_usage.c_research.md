# sources/storage-engines/sqlite/tool/index_usage.c

## Purpose
`index_usage.c` analyzes a workload log and reports how often each index in a database schema is selected by SQLite's query planner. It helps identify unused or heavily used indexes for a given SQL corpus.

## Important APIs, Types, and Functions
`usage()` prints expected database and log schema. `main()` uses SQLite APIs to open the schema database, create a temp `idxu` table of indexes and counters, attach the log database, prepare `EXPLAIN QUERY PLAN` for each logged statement, parse detail text for `USING INDEX`, increment counters, and print a report with indexed columns from `pragma_index_info()`.

## Control Flow
The program parses `--progress N`, `-q`, `--using NAME`, and positional `DATABASE LOG`. It opens the database read-only, validates schema access, creates temp tracking state, attaches `LOG`, selects non-transaction/non-pragma SQL from `log.sqllog`, and for each compilable statement walks the EQP rows. When an index use is detected, it optionally prints the SQL for `--using`, increments the counter, and continues. Finally it prints indexes ordered by count descending.

## State and Persistence
The main database is opened read-only, but SQLite temp state is created on the connection. The log database is attached read-only only if SQLite enforces it from the main open flags and VFS; the code itself just uses `ATTACH %Q`. No persistent schema or log changes are intended.

## Dependencies and Integration Points
It depends on SQLite, `sqlite_schema`, `EXPLAIN QUERY PLAN` output text, and a log database with `sqllog(sql TEXT)`. It integrates with workload capture and schema tuning workflows.

## Risks
The parser depends on human-readable EQP detail text containing `USING INDEX`, which can change across SQLite versions and misses covering-index or automatic-index text variants if wording differs. It filters statements by the first five uppercase characters, a simple heuristic. Statements with side effects are only prepared as `EXPLAIN QUERY PLAN`, not run, but invalid SQL is counted as an error unless quiet. Index-name extraction scans until a character before `(` in a fragile way.

## Test Signals
Use a known schema and log where specific queries should use specific indexes, compare `--using NAME` output, verify progress messages, test invalid SQL with and without `-q`, and run across SQLite versions to detect EQP text drift.
