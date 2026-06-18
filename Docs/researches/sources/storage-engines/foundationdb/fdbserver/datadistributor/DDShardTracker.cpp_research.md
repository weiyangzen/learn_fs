# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDShardTracker.cpp`

## Purpose

This file implements shard metric tracking, shard splitting/merging, read-hot detection, metric query serving, storage-queue rebalance triggering, bulk-load shard boundary setup, and physical-shard collection maintenance for the data distributor. It decides when shard boundaries should change and sends `RelocateShard` requests to the relocation queue.

## Important APIs, Types, and Functions

- `getBandwidthStatus()` and `getReadBandwidthStatus()` classify write/read pressure from `StorageMetrics`.
- `updateMaxShardSize()` updates an `AsyncVar<Optional<int64_t>>` as estimated database size changes.
- `calculateShardSizeBounds()` computes dynamic shard bounds and flags read-hot shards.
- `trackShardMetrics()` waits on `IDDTxnProcessor::waitStorageMetrics()`, updates per-shard metrics, database/system size estimates, physical-shard metrics, and can emit move-out relocations for oversized/anonymous physical shards.
- `shardUsableRegions()` audits usable-region coverage from `ShardsAffectedByTeamFailure` and emits populate-region relocation if a shard has too few usable regions.
- `shardSplitter()`, `executeShardSplit()`, `shardMerger()`, and `shardEvaluator()` implement split/merge decisions and boundary changes.
- `restartShardTrackers()` replaces tracker actors for affected key ranges and starts metric, split/merge, and optional usable-region actors.
- `trackInitialShards()` initializes trackers from `InitialDataDistribution`, respecting user range boundaries, then sends `readyToStart`.
- `fetchShardMetrics()`, `fetchTopKShardMetrics()`, and `fetchShardMetricsList()` serve queue/rebalance metric requests with timeout behavior.
- `triggerStorageQueueRebalance()` selects a high-write shard from affected teams and emits `REBALANCE_STORAGE_QUEUE`.
- `DataDistributionTrackerImpl::run()` wires long-running services for logging, read-hot detection, metric streams, storage-queue requests, bulk-load shard requests, restart requests, and child actor errors.
- `trackKeyRangeInPhysicalShardMetrics()` and `PhysicalShardCollection::*` maintain physical-shard-to-team, key-range-to-physical-shard, metric, cleanup, and logging structures.

## Control Flow

Startup calls `DataDistributionTracker::run()`, stores stream handles and configuration snapshots, and delegates to `DataDistributionTrackerImpl::run()`. Initialization creates shard trackers for all initial shard intervals, splitting at user range boundaries. `readyToStart` is sent after tracker installation and initial size accounting begins; the max-shard-size updater starts after initial metrics are collected.

Each tracked shard has a metrics actor and a shard evaluator actor. The metrics actor waits until observed metrics leave the current bounds, updates estimates and `ShardMetrics`, and triggers read-hot or physical-shard move-out signals when needed. The evaluator waits for stats and max-shard-size availability, then repeatedly calculates whether the shard should split, merge, or wait for metric changes. Splits call `splitStorageMetrics()`, restart trackers in a nibbling order compatible with the relocation queue, define new shards in `ShardsAffectedByTeamFailure`, and emit split relocations for all but the kept subrange. Merges collect adjacent low-bandwidth shards forward and backward while respecting system boundaries, user range boundaries, bulk-load ranges, shard-count limits, max shard size, and low-bandwidth coalescing delay; successful merges restart one tracker and emit a merge relocation.

Metric request handlers aggregate metrics over intersecting tracked ranges, waiting for missing stats when possible and returning fallback/timed-out replies when necessary. Background service actors multiplex these request handlers with logging, read-hot range logging, storage-queue rebalance triggers, bulk-load shard boundary creation, and restart requests from failure tracking.

Physical-shard maintenance is updated from both metric tracking and relocation completion. The collection can initialize/restored physical shard mappings, select reusable physical shards for a primary team, find paired remote teams, generate new IDs, update metrics on key-range moves, detect anonymous-shard transition work, detect oversized physical shards, remove empty physical shards, and log physical-shard/team/server distributions.

## State and Persistence Behavior

The tracker owns in-memory range state through `KeyRangeMap<ShardTrackedData>* shards`, per-shard `AsyncVar<Optional<ShardMetrics>>`, `dbSizeEstimate`, `systemSizeEstimate`, `maxShardSize`, and child actors. Durable reads come through `IDDTxnProcessor` metric APIs and bulk-load metadata reads. Boundary changes are represented in memory immediately by restarting trackers and defining shards, then made durable indirectly by emitted `RelocateShard`s that the queue turns into `moveKeys()` operations. `PhysicalShardCollection` is in-memory bookkeeping keyed by data-move/physical-shard IDs; it is reconstructed or updated from data distribution metadata and relocation completion paths rather than writing directly here.

## Dependencies and Integration Points

This file integrates with `DDShardTracker.h`, `DDSharedContext.h`, `DataDistribution.h`, `ShardSizing`, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, and `IDDTxnProcessor`. It emits relocation requests consumed by `DDRelocationQueue`, serves metric streams used by queue destination selection and background rebalancing, uses `anyZeroHealthyTeams` to suppress merges when no healthy teams exist, and uses Flow actor/task priorities and trace events for scheduling and observability.

## Risks and Edge Cases

Shard-boundary correctness is sensitive to ordering. `executeShardSplit()` deliberately avoids asking the queue to split one shard into three pieces at once. Merges must not cross `systemKeys` boundaries, user range config boundaries, or active bulk-load ranges. Metric unavailability can stall decisions; timeout fallbacks can return intentionally large metrics to avoid unsafe movement. Physical-shard metrics are approximate in some multi-shard/move-out paths, including even division across multiple outgoing physical shards. `SafeAccessor` protects actors from accessing a destroyed tracker, but any missed guard could be a use-after-free risk. Bulk-load ranges temporarily disable normal boundary changes to avoid disrupting load tasks.

## Test Signals

Local tests include `/DataDistributor/Tracker/FetchTopK`, currently a minimal empty-range timeout/result test, and `/DataDistributor/Tracker/CrossesCriticalSystemBoundary`, which covers the system-key boundary predicate used by merge feasibility. Many important behaviors rely on simulation/integration coverage and trace probes: split/merge trace events, `DDTrackerStats`, read-hot logs, storage-queue rebalance traces, physical-shard consistency assertions in simulation, and code probes for shard split/merge paths.
