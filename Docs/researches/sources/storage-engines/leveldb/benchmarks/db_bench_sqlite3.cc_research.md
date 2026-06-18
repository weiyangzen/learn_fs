<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc

## Purpose
SQLite benchmark executable that mirrors LevelDB benchmark workloads for comparative key/value performance.

## Important APIs, Types, And Functions
Global `FLAGS_*` cover benchmark list, num/reads/value size, histogram, compression ratio for value generation, page/cache settings, existing DB, rowids, transaction, WAL, and DB path. Class `Benchmark` implements open, write, random/sequential read, and reporting.

## Control Flow
`main()` parses flags. `Benchmark::Run()` opens SQLite, tokenizes benchmark names, runs fresh/existing write or read operations, checkpointing WAL after writes. `Write()` prepares REPLACE and optional transaction statements; `Read()` prepares keyed SELECTs; `ReadSequential()` scans ordered keys.

## State And Persistence Behavior
Creates `dbbench_sqlite3-*.db` files in the LevelDB test directory, deletes old files unless reusing, manages SQLite connection and prepared statements, WAL checkpoints, cache/page PRAGMAs, and histogram counters.

## Dependencies And Integration Points
Requires sqlite3 plus LevelDB utility classes for `Env`, `Slice`, `Histogram`, `Random`, and test data generation. Optional CMake benchmark target linked to sqlite3 and run by CI on non-Windows runners for comparative performance baselines.

## Risks
Error handlers exit the process; destructor always closes `db_`; fresh benchmarks reopen DBs and skip when `--use_existing_db` conflicts; SQL statements use blob keys and optional WITHOUT ROWID, so results differ from LevelDB beyond storage engine alone.

## Test Signals
Outputs micros/op, MB/s, optional histograms, and hard exits on SQLite prepare/step/finalize failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc -->
