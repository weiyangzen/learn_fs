## sources/storage-engines/sqlite/test/speedtest1.c

### Purpose
`speedtest1.c` is SQLite's standalone performance benchmark driver. It creates deterministic data sets, runs named SQL workload suites, times each test case, optionally emits the SQL instead of executing it, and can produce verification hashes and memory/page-cache statistics for comparison across SQLite builds and compile options.

### Important APIs, types, and functions
The central state is the global `g` structure, holding the SQLite handle, current prepared statement, timing totals, option flags, result hash state, pseudo-random generator state, SQL script output, and configurable schema fragments such as `WITHOUT ROWID`, `STRICT`, `NOT NULL`, and `PRIMARY KEY`. Utility APIs include `integerValue()`, `speedtest1_timestamp()`, deterministic `speedtest1_random()`, `swizzle()`, `speedtest1_numbername()`, and the SQL wrappers `speedtest1_exec()`, `speedtest1_once()`, `speedtest1_prepare()`, and `speedtest1_run()`. Benchmark suites are implemented by `testset_main()`, `testset_cte()`, `testset_fp()`, `testset_star()`, `testset_app()`, `testset_rtree()`, `testset_orm()`, `testset_trigger()`, `testset_json()`, `testset_parsenumber()`, and `testset_debug1()`.

### Control flow
`main()` parses options, configures SQLite before initialization where required, deletes and opens the target database or memory database, applies PRAGMAs and custom functions, expands the `mix1` macro testset, and runs each selected testset. Between multiple testsets it drops all main and temp tables. Each individual benchmark calls `speedtest1_begin_test()`, performs SQL work through shared wrappers, and finishes with `speedtest1_end_test()`. `speedtest1_final()` prints aggregate timing and verification data.

### State and persistence behavior
The program mutates a target database file unless `--memdb` is used. It explicitly removes existing database files through the selected VFS and `unlink()`, changes pager and schema behavior with PRAGMAs, and can write SQL scripts and verification output files. `--verify` hashes result streams, omitting exact floating-point values to reduce platform variance. The pseudo-random sequence is reset per test, making workloads reproducible.

### Dependencies and integration points
This file integrates directly with the public SQLite C API, optional R-Tree APIs, VFS time and delete methods, Linux `/proc/PID/io` for stats, optional checksum VFS registration, deprecated trace hooks, and build-time feature macros. It is wired into SQLite build targets for comparing current and historical amalgamations.

### Risks and test signals
Risks include option-order sensitivity for `sqlite3_config()`, benchmark results changing with compile-time features, SQL-only paths masking execution errors, intentionally relaxed settings such as `synchronous=OFF`, and very large generated databases at high `--size`. Strong signals are nonzero exit on SQLite errors, stable verification hash output, `PRAGMA integrity_check`, optional statement scan status and memory statistics, and deterministic test numbering/timing output.
