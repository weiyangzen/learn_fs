# sources/storage-engines/sqlite/test/optfuzz.c

## Purpose

`optfuzz.c` is a standalone optimizer correctness fuzz harness. It runs fuzzer-generated SQL against a fixed in-memory database twice, once with one optimizer setting and once with the opposite setting, then reports a failure if normalized output differs.

## Important APIs, Types, and Functions

It includes `sqlite3.c` with `SQLITE_THREADSAFE=0` and `SQLITE_OMIT_LOAD_EXTENSION=1`, then includes `optfuzz-db01.c`. Key functions are `prepare_sql()`, `run_sql()`, `optfuzz_exec()`, `readFile()`, and `main()`. `optfuzz_exec()` renders result rows into text, sorts rows per statement through a staging table, and stores statement markers plus grouped output in `opt` or `noopt` tables.

## Control Flow

`main()` parses `--output-trace` and `--valid-sql`, opens two in-memory DBs, deserializes `data001` into `dbRun`, and processes each input file. Normal mode runs the SQL with `SQLITE_TESTCTRL_OPTIMIZATIONS` set to `0`, stores output in `opt`, then sets the mask to `0xffff`, stores output in `noopt`, and compares `group_concat(x,char(10))` across both tables. Mismatches print both outputs and exit non-zero.

## State and Persistence Behavior

All databases are in memory. `dbRun` is initialized from a read-only fixture; `dbOut` accumulates comparison tables. Input SQL is allocated with SQLite memory APIs. Output tables are not dropped between files, so multi-file comparisons are cumulative unless the process is restarted.

## Dependencies and Integration Points

The harness uses SQLite amalgamation internals, `sqlite3_deserialize()`, `sqlite3_test_control()`, and the embedded `data001` fixture. It integrates with SQL fuzzers as a differential oracle for optimizer behavior.

## Risks and Test Signals

Sorting row strings makes the oracle order-insensitive and can hide order regressions. Very wide rows intentionally fail at about 4000 rendered bytes. SQL write/transaction effects are partly contained by `ROLLBACK` before each file. Signals include `<file>: <nStmt> stmts <nRow> rows ok`, optimized/non-optimized errors, mismatch output, excessive row line errors, and final memory-leak diagnostics.
