# sources/storage-engines/tikv/components/engine_traits/src/snapshot.rs

Purpose: Defines the generic snapshot trait for consistent read-only engine views.

Important APIs and control flow: `Snapshot` is a marker-style trait requiring `'static`, `Peekable`, `Iterable`, `CfNamesExt`, `SnapshotMiscExt`, `Send`, `Sync`, `Sized`, and `Debug`. It provides a default `in_memory_engine_hit` hook returning false.

State, persistence, and dependencies: Implementors hold backend snapshot state that pins a read view; no new data is persisted through this trait.

Integration points, risks, and test signals: Used by TiKV read paths and shared iterator/read tests. Risks include lifetime pressure from `'static`, inability to clone snapshots directly, cache-hit reporting differences, and ensuring iterators/readers share the same snapshot view. Snapshot tests verify point-read and post-write isolation.
