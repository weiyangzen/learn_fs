<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench.cc

## Purpose
Primary LevelDB microbenchmark executable for writes, reads, deletes, seeks, compaction, compression, CRC, stats, heap profile, threading, cache/filter/options variants.

## Important APIs, Types, And Functions
Global `FLAGS_*` tune operation list, record counts, threads, value size, cache, Bloom bits, compression, DB path, etc.; helper classes `CountComparator`, `RandomGenerator`, `KeyBuffer`, `Stats`; shared structs `SharedState`, `ThreadState`; class `Benchmark` with methods for each operation.

## Control Flow
`main()` parses flags and chooses a temp DB. `Benchmark::Run()` opens the DB, tokenizes `FLAGS_benchmarks`, maps names to member functions, resets per-run options, optionally recreates fresh DBs, and calls `RunBenchmark()` which starts synchronized threads and merges stats.

## State And Persistence Behavior
Creates/removes a LevelDB database under `FLAGS_db`, heap profile files, optional cache/filter policy objects, and per-thread deterministic random state. Fresh write benchmarks destroy/reopen the DB unless `--use_existing_db` is set.

## Dependencies And Integration Points
Depends on LevelDB DB/Env/Cache/Comparator/FilterPolicy/WriteBatch APIs, `port` compression helpers, crc32c, histogram, random/test utilities, and POSIX `/proc/cpuinfo` on Linux. Built by `leveldb_benchmark()` in CMake and run in CI. Exercises public APIs and internal performance properties such as comparator count and DB properties `leveldb.stats`/`leveldb.sstables`.

## Risks
Benchmark exits process on DB errors; random overwrite/read workloads may report misses depending on prior benchmark sequence; duplicate `readrandomsmall` branch is harmless but suspicious; results depend heavily on optional compression libraries and build flags.

## Test Signals
Produces throughput, micros/op, optional histograms, comparison counts, and explicit errors on failed DB operations. CI runs default benchmark sequence.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench.cc -->
