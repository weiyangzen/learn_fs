# sources/storage-engines/rocksdb/tools/write_stress.cc

## Purpose

Implements a focused RocksDB stress binary for compaction, flush, obsolete-file deletion, iterator file retention, WAL sync, and table-cache reopen behavior. It is designed to be repeatedly run and killed by `write_stress_runner.py`.

## Important APIs, Control Flow, And Dependencies

With `GFLAGS` unavailable the binary exits with an installation message. With gflags, flags configure key/value sizes, DB path, DB destruction, runtime, RNG seed, prefix mutation periods/probabilities, iterator hold time, sync probability, full-scan obsolete-file deletion, and low-open-files mode. `WriteStress` opens a DB with small write buffers, small target files, many flush/compaction threads, optional `max_open_files=20`, and optional immediate obsolete-file deletion. `Run` starts three threads: `WriteThread` repeatedly writes random keys under a mutable 3-byte prefix; `PrefixMutatorThread` periodically mutates prefix characters at different rates; `IteratorHoldThread` holds an iterator for several seconds before scanning it.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state is the stress DB, which may survive across runs when `--destroy_db=false`. The key prefix and stop flag are atomic state shared by threads. At clean shutdown, the tool pauses background work, gathers live SST file numbers from metadata, lists DB directory children, and aborts if it finds a table file not present in live metadata, then resumes background work. Dependencies include RocksDB DB/options/env/iterator APIs, `ParseFileName`, `SystemClock`, `port::Thread`, random generators, and gflags. Risks include intentionally harsh concurrency, infinite runtime when `--runtime_sec=-1`, abort-on-error semantics, deprecated option names in newer RocksDB versions, and no leak check when the runner kills the process. Test signals are process exit status and absence of orphaned table files after clean runs.
