# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DDSharedContext.h

Purpose: declares the shared context object passed among DD components. It centralizes the distributor identity, interface, lock, configuration, enable state, tracker cancellation flag, shard-failure index, tracker, DD queue, and primary/remote team collections.

Important APIs and types: `DDSharedContext` owns `DDEnabledState`, `DataDistributorInterface`, `UID ddId`, `MoveKeysLock`, `DatabaseConfiguration`, `Reference<ShardsAffectedByTeamFailure>`, `Reference<DataDistributionTracker>`, `Reference<DDQueue>`, and `Reference<DDTeamCollection>` for primary and remote. It exposes constructors, `id()`, `markTrackerCancelled()`, `isTrackerCancelled()`, `usableRegions()`, and `isDDEnabled()`.

Control flow: this header only declares lifecycle. Components share a reference to the same context; cancellation is signaled by flipping `trackerCancelled`, and DD enablement delegates to the shared `DDEnabledState`.

State and persistence: the context is in-memory orchestration state. The underlying `DDEnabledState` is intentionally a non-resettable unique pointer because it is shared with the snapshot server. Durable state remains in system keys and data-movement metadata handled elsewhere.

Dependencies and integration: includes `DataDistributorInterface`, `MoveKeys`, `DDShardTracker`, `ShardsAffectedByTeamFailure`, and `DDTeamCollection`. It is the glue object used by real and mock data distributor startup paths.

Risks: because the class is intentionally small but shared broadly, adding members can create hidden coupling. Raw cancellation state must outlive actors that read it through `DataDistributionTracker::SafeAccessor`. Ordering between context destruction and component actors is important.

Test signals: tests should ensure constructors initialize shared state consistently, tracker cancellation is visible to actors, and mock/real DD paths share the same context contracts.
