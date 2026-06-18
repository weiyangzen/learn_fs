# sources/storage-engines/badger/value_gc_rewrite_bench_test.go

## Purpose
This benchmark measures value-log GC rewrite performance when early log files contain many expired entries followed by live entries. It targets the cost of `valueLog.rewrite` on an expired-heavy candidate file.

## Important APIs, Types, And Functions
Constants define expired/live key counts, value size, value-log file size, threshold, and expiry. `benchmarkValueGCRewriteOptions` tunes Badger for stable rewrite benchmarking and disables compaction/metrics noise. `benchmarkWriteEntries` writes entries in transactions and handles `ErrTxnTooBig` by committing and continuing. `benchmarkPrepareRewriteFixture` builds a reusable fixture DB. `copyDir` clones the fixture for each iteration. `BenchmarkValueGCRewriteExpiredOnlyFile` performs the timed rewrite.

## Control Flow
The benchmark builds one fixture outside the timed loop, then for each `b.N` iteration copies it to a fresh run directory, opens DB, selects the first sorted vlog fid, times `db.vlog.rewrite(lf)`, closes DB, and removes the run directory.

## State And Persistence Behavior
It creates real Badger directories and value logs. The per-iteration copy preserves identical persisted state, making rewrite timing independent of fixture construction. The measured rewrite may rewrite live entries and delete the old vlog in the copied run.

## Dependencies And Integration Points
It integrates with Badger option setup, transaction write paths, value-log file selection under `filesLock`, and filesystem copy/removal. It intentionally avoids metrics to reduce benchmark overhead.

## Risks And Edge Cases
`copyDir` rejects non-regular files, so symlinks or special files in fixtures would fail. The benchmark assumes at least two vlog files and direct access to internal `vlog.filesMap`. Results include DB open/close and directory copy outside timing but may still be affected by filesystem cache.

## Test Signals
The primary signal is allocation and time cost of `rewrite` when expired entries should be skipped cheaply. It complements `TestValueGCRewriteSkipsLSMGetOnlyForExpiredEntriesInMixedVlogFile`.
