# sources/storage-engines/tikv/src/server/gc_worker/compaction_runner.rs

## Purpose

This file implements the automatic compaction runner. Unlike classic automatic GC, it does not directly scan and GC every region. Instead, it periodically evaluates regions using RocksDB table properties and optional MVCC read-activity signals, ranks compaction candidates, and manually compacts write/default CF ranges to let compaction filters reclaim space and improve read performance.

## Important APIs, Types, And Functions

- `CompactionCandidate` stores score, tombstone count, estimated discardable MVCC entries, total entries, row count, MVCC read versions scanned, and region metadata. Ordering is score-based for heap ranking.
- `CompactionRunnerHandle` owns the thread join handle and stop-signal sender.
- `CompactionRunner<S, R, E>` owns a safe point provider, region info provider, KV engine, stop receiver, stopped flag, and `GcWorkerConfigManager`.
- `start` spawns the runner on the `COMPACTION_RUNNER_THREAD` thread name and preserves thread-group properties.
- `run` polls config and safe point, collects candidates, compacts candidates, resets the MVCC read tracker, and sleeps until the next interval or stop signal.
- `collect_compaction_candidates` walks regions with `seek_region`, evaluates each one, and keeps a bounded top-N min heap based on check interval.
- `evaluate_range_candidate` reads write-CF table properties for a region, estimates tombstones and discardable versions, pulls MVCC read tracker data when enabled, and returns a scored candidate.
- `get_compact_score` applies tombstone or redundant-row thresholds and optionally adds weighted MVCC-read pressure.
- `compact_candidate` compacts write CF first, then default CF, with configurable bottommost-level force.

## Control Flow

The runner loop exits on stop. Each round clones a consistent config snapshot, reads the current GC safe point, skips work if the safe point is zero, then scans region metadata from the beginning of the keyspace. Candidate collection evaluates each region and retains only the best candidates to keep memory bounded. Candidate compaction rechecks each region with the current safe point before compaction, skips candidates no longer needing work, then invokes manual range compaction for write and default CF. The loop accounts for elapsed time and enforces a minimum 20-second inter-round gap when MVCC-read-aware scoring is enabled, giving the read tracker time to accumulate new observations after reset.

## State And Persistence Behavior

The runner holds no durable state. It mutates engine state indirectly via manual `compact_range_cf`, causing RocksDB to rewrite SST files and activate compaction filters. Metrics gauges and histograms record candidate counts, scores, tombstone/discardable distributions, MVCC read signals, and evaluation/compaction durations. Test/failpoint builds expose `FIRST_COMPACTION_CANDIDATE_REGION`.

## Dependencies And Integration Points

The runner depends on `GcSafePointProvider`, `RegionInfoProvider`, `KvEngine` table properties and manual compaction APIs, key encoding helpers, `GcWorkerConfigManager`, MVCC read tracker, Prometheus metrics, and failpoints. `GcWorker::start_auto_compaction` constructs it after initializing the global MVCC read tracker.

## Risks

- Region scanning uses synchronous `mpsc` callbacks around `seek_region`; provider stalls can block the runner.
- Score estimates are property-based and approximate timestamp distribution linearly between oldest/newest stale/delete timestamps.
- `num_entries - mvcc_properties.num_versions` assumes properties are internally consistent.
- `PartialOrd` over `f64` can encounter NaN; `Ord` maps unordered comparisons to `Equal`, which can affect heap ordering.
- If compactions are faster than expected, heap capacity derived from check-interval seconds may underutilize opportunities; if slower, the interval guard truncates processing.
- Manual compaction of both write and default CF can be IO-expensive and shares resources with foreground traffic.

## Test Signals

The file itself contains failpoints rather than normal tests. Failpoints mark thread start, runner start, candidate detection, candidate collection, specific table-property candidate shapes, and first-candidate selection. External tests can verify MVCC-aware prioritization through `FIRST_COMPACTION_CANDIDATE_REGION`.
