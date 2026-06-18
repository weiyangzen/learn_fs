# sources/storage-engines/sqlite/test/kvtest.c

## Purpose

`kvtest.c` is a standalone key/value BLOB benchmark comparing SQLite BLOB storage/access against one-file-per-BLOB filesystem storage. It can initialize a test database, export BLOBs to files, report database statistics, and run timed read/update workloads.

## Important APIs, Types, and Functions

CLI commands are `init`, `export`, `stat`, and `run`. `initMain()` creates `kv(k INTEGER PRIMARY KEY, v BLOB)` with random blobs. `exportMain()` writes rows to flat or tree file layouts. `statMain()` reports row sizes, page stats, freelist count, and integrity check. `runMain()` benchmarks direct files, SQL reads/updates, or incremental `sqlite3_blob` reads/writes. Helpers include `pathType()`, `fileSize()`, `randInt()`, `readFile()`, `updateFile()`, `timeOfDay()`, `display_stats()`, and `rememberFunc()`.

## Control Flow

`main()` dispatches by command. `init` parses count/size/variance/page-size options and bulk inserts `randomblob()` rows in one transaction. `export` scans `SELECT k, v FROM kv ORDER BY k`, formats filenames from keys, creates subdirectories if `--tree` was requested, and writes raw BLOB bytes. `run` classifies the target as DB or directory, configures DB pragmas (`mmap_size`, `cache_size`, `synchronous`, journal mode, WAL checkpoint behavior), optionally begins a transaction, then loops through ascending/descending/random keys performing file I/O, incremental BLOB I/O, or SQL. It reports elapsed time, microseconds per BLOB, and throughput.

## State and Persistence Behavior

`init` rewrites a DB. `export` creates files/directories. `run --update` mutates either DB BLOBs or exported files while preserving sizes. DB runs affect journal mode, cache/mmap/sync settings, transaction state, and optionally WAL checkpointing.

## Dependencies and Integration Points

It depends on SQLite amalgamation plus standard filesystem APIs, with Windows compatibility shims and optional Linux `/proc/PID/io` stats. It exercises SQLite pager, mmap, WAL/rollback journal, SQL update/read, and incremental BLOB paths.

## Risks and Test Signals

Risks include broad DB file classification by size multiple of 512, an inaccurate `readFile()` nul-terminator comment, a likely `--mmap` validation typo checking `nCount`, fixed filesystem naming limits, and sparse key ranges extending runs. Signals include successful `stat` integrity checks, expected row counts/sizes, successful export, timing output for all access modes, `--stats` counters, and `--integrity-check` output.
