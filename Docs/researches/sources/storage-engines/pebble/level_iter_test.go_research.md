# sources/storage-engines/pebble/level_iter_test.go

Purpose: this file provides datadriven tests and benchmarks for v1 `levelIter`, covering file selection, per-table bounds, range-deletion interleaving, prefix seek behavior, and performance-sensitive seek/scan patterns.

Important APIs/types/functions: `TestLevelIter` uses fake per-file iterators to test basic commands and table-load bounds. `levelIterTest` builds real SSTables in memory and exposes `newIters`, `runClear`, and `runBuild`. `TestLevelIterBoundaries` exercises boundary behavior over real SSTables and can save an iterator across commands. `levelIterTestIter` wraps `levelIter` to expose the separate range-delete iterator state to `itertest`. `TestLevelIterSeek` drives seek-focused datadriven cases and iterator stats. `buildLevelIterTables` plus the benchmark functions create multi-file SSTable levels for performance tests.

Control flow: fake tests parse `define` lines into `base.InternalKV` slices and manifest metadata, then run `itertest.RunInternalIterCmd`. Real-SSTable tests parse input into point keys, range deletions, and range keys, write raw SSTables, derive `TableMetadata`, and then instantiate `levelIter` over a sorted `LevelSlice`. Range-delete tests initialize `initRangeDel` with a setter so seeks can also position an external range tombstone iterator. Benchmarks repeatedly perform random seeks, sequential bounded scans, prefix seeks with and without `TrySeekUsingNext`, and forward/backward iteration.

State and persistence behavior: state is held in memory through `vfs.NewMem`, SSTable readers, metadata slices, and optional saved iterator instances. Tests close readers and iterators explicitly. No durable repo state is modified.

Dependencies and integration points: depends on `datadriven`, `itertest`, manifest slices, raw SSTable writer/reader APIs, bloom filters, range deletion and range key encoders, block read stats, object storage file wrappers, and test key comparers.

Risks and test signals: datadriven output is sensitive to iterator formatting and boundary key behavior. The tests are valuable for regressions around skipped files, bound propagation, prefix bloom filtering, range-delete handoff, and lazy file loading. Benchmarks serve as signals for regressions in common CockroachDB-like workloads such as repeated bounded scans and monotonic prefix seeks.
