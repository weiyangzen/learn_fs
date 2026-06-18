# sources/storage-engines/tikv/components/hybrid_engine/src/engine.rs

Purpose: container for a complete disk `KvEngine` and a selective `RegionCacheEngine`.

Important APIs/types/functions: `HybridEngine::new`, `region_cache_engine`, test-only `new_snapshot`, `disk_engine`, and `SnapshotContext`.

Control flow: test snapshot helper takes a disk snapshot and optionally acquires a cache snapshot when the cache is enabled and context has a valid region/read timestamp.

State and persistence: owns engine handles; persistence belongs to disk engine, cache residency to region cache engine.

Dependencies/integration: generic over `engine_traits::KvEngine` and `RegionCacheEngine`; exported by crate root.

Risks: `new_snapshot` is test-only and unwraps region context; production snapshot flow is observer based.

Test signals: tests verify cache snapshot availability under safe point/read-ts and config disabling.
