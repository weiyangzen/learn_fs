# sources/storage-engines/pebble/replay/replay_test.go

## Purpose
This file is the main datadriven and regression test harness for Pebble workload replay. It builds captured workloads, replays them through `Runner`, validates replayed DB contents, exercises pacing modes, and covers capture/replay variants for ordinary flushes, value separation, ingestion, and ingest-and-excise metadata.

## Important APIs, Types, and Functions
`runReplayTest` interprets datadriven commands such as `corpus`, `replay`, `scan-keys`, `wait-for-compactions`, `wait`, and `close` over a shared in-memory VFS. It constructs `Runner` with `RunDir`, `WorkloadFS`, `WorkloadPath`, `Pacer`, and test `pebble.Options`.

`TestReplay`, `TestReplayPaced`, `TestReplayValSep`, and `TestReplayIngest` are thin entry points over separate replay testdata files.

`TestLoadFlushedSSTableKeys` validates that flushed SSTable contents can be loaded into a batch representation, including point keys, range deletions, range key sets/unsets/deletes, and blob-aware reader provider setup.

`collectCorpus` builds workload directories from datadriven corpus scripts. It drives `WorkloadCollector`, `Checkpoint`, `Flush`, `Ingest`, `IngestAndExcise`, file creation, file discovery, and manifest-start discovery.

`TestBenchmarkString` verifies benchmark metric formatting from `Metrics`.

`TestCompactionsQuiesce` and `TestFlushEndNotifiesRefreshMetrics` are hang-regression tests around replay completion and metric refresh signaling.

`buildFlushOnlyWorkload`, `getHeavyWorkload`, and `buildHeavyWorkload` synthesize replay workloads with controlled flush and compaction behavior.

## Control Flow
The replay tests first build or clone a workload checkpoint into a run directory, configure deterministic DB options, start a `Runner`, then inspect output through iterators, filesystem listings, or `Runner.Wait`. Corpus capture tests open a DB with a `WorkloadCollector`, start capture after checkpointing, mutate the DB, wait for collector copy completion, and stop collection.

`TestLoadFlushedSSTableKeys` tracks flushed table numbers through `FlushEnd`, flushes the DB, sets up a blob reader provider, calls `loadFlushedSSTableKeys`, and then decodes the resulting batch with `batchrepr`.

The quiescing tests run replay asynchronously and use `require.Eventually` to detect deadlocks in `Wait`, with timeout adjustments for slow or invariants builds.

## State and Persistence Behavior
All persistence is modeled through `vfs.MemFS`, cloned checkpoints, manifest and SST files, and captured workload directories. The collector tests depend on copied manifests, SSTables, and blob files matching original source files. The heavy workload cache uses `sync.Once` to avoid rebuilding expensive test data.

## Dependencies and Integration Points
The file integrates with Pebble `DB`, batches, iterators, `WorkloadCollector`, replay `Runner`, `Pacer` implementations, `sstable` writer test helpers, range-key decoding, blob reader provider setup, and `datatest` batch/SST command utilities. It uses `datadriven` files under replay testdata as the behavioral contract.

## Risks
The tests are sensitive to deterministic file names, manifest sizes, iterator stack selection, compaction scheduling, and timing around asynchronous replay and collector goroutines. Randomized heavy workload generation makes compaction coverage realistic but requires generous eventual timeouts. Value-separation replay relies on captured blob-reference files being copied by the collector.

## Test Signals
Strong coverage exists for replay success, paced replay, value separation, ingestion, corpus capture, batch reconstruction from SSTables, benchmark output formatting, quiescence termination, and flush-only metric notification. Failures usually indicate replay ordering bugs, collector copy omissions, manifest parsing issues, or missed completion notifications.
