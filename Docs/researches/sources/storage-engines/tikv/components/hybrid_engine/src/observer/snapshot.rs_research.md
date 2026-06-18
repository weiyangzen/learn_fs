# sources/storage-engines/tikv/components/hybrid_engine/src/observer/snapshot.rs

Purpose: snapshot observer that pins region-cache snapshots during raftstore snapshot creation and records cache snapshot usage/fallback metrics.

Important APIs/types/functions: `RegionCacheSnapshotPin::{take,drop}`, `HybridSnapshotObserver::{new,register_to}`, and `SnapshotObserver::on_snapshot`.

Control flow: `on_snapshot` converts a region to `CacheRegion` and asks `RegionCacheMemoryEngine` for a snapshot using read ts and disk sequence number. `take` returns successful cache snapshots or records fallback reasons; dropping unused successful pins records `wasted`.

State and persistence: holds an optional cache snapshot result that pins cache data until consumed or dropped.

Dependencies/integration: used by `HybridEngineSnapshot::from_observed_snapshot`; integrates `engine_traits::FailedReason`, in-memory engine snapshots, raftstore snapshot observer, and metrics.

Risks: downstream downcast assumes this exact pin type; unused successful pins may indicate over-acquisition overhead.

Test signals: indirectly covered by snapshot availability/fallback tests.
