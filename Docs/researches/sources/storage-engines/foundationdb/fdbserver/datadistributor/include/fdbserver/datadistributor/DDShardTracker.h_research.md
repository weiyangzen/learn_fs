# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDShardTracker.h

Purpose: declares the shard tracker interface and concrete `DataDistributionTracker` state holder. The tracker watches shard sizes, metrics, hot ranges, physical shards, and bulk-load constraints, then emits `RelocateShard` work to the DD queue.

Important APIs and types: `IDDShardTracker` exposes readiness and request streams for shard metrics, top-K metrics, metrics lists, average shard bytes, storage-queue rebalance triggers, and bulk-load triggers. `DataDistributionTrackerInitParams` packages dependencies. `DataDistributionTracker` stores transaction processor, distributor ID, shard map pointer, actor collection, DB size/max-shard estimates, output stream, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, cancellation guard, read-hot stream, and user range config. Static `run()` wires external streams into the actor implementation.

Control flow: this header does not implement tracking, but it declares the lifecycle: construct from init params, run with initial data and request streams, update internal estimates, and answer synchronous `getAverageShardBytes()`. `SafeAccessor` is used by long-lived actors to avoid accessing a tracker after cancellation.

State and persistence: in-memory tracker state points at a longer-lived `KeyRangeMap<ShardTrackedData>`. Persistence is external: initial data comes from `InitialDataDistribution`, moves go through data-movement metadata, and user range config snapshots come from DD configuration.

Dependencies and integration: depends on `DataDistribution.h`, `IDDTxnProcessor`, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, Flow streams, and DD queue relocation output. `DDSharedContext` owns a tracker reference.

Risks: `shards` and `trackerCancelled` are raw pointers with lifetime assumptions; misuse can become memory unsafe. `getAverageShardBytes()` assumes `maxShardSize` is present. Actor cancellation ordering is central, hence the explicit safe accessor and destructor.

Test signals: tests should validate cancellation, request stream service, average shard bytes updates, bulk-load gating, storage-queue rebalance triggers, and physical-shard relocation decisions. This header itself provides no unit tests.
