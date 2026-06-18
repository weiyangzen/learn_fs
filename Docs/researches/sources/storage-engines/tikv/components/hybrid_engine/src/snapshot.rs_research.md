# sources/storage-engines/tikv/components/hybrid_engine/src/snapshot.rs

Purpose: hybrid read snapshot that routes data-CF reads/iterators to the region cache when available and falls back to disk otherwise.

Important APIs/types/functions: `HybridEngineSnapshot`, `from_observed_snapshot`, `Iterable`, `Peekable`, `Snapshot`, `CfNamesExt`, and `SnapshotMiscExt` impls.

Control flow: construction stores disk snapshot plus optional cache snapshot. Point reads and iterators check `is_data_cf`; data CF uses cache if present, all other CFs use disk. Observed snapshot conversion downcasts a `RegionCacheSnapshotPin` and takes its cache snapshot.

State and persistence: read-only snapshot state; disk snapshot supplies sequence number and CF names.

Dependencies/integration: uses hybrid vector/iterator wrappers, in-memory snapshot pins, raftstore observed snapshots, and engine traits.

Risks: downcast unwrap requires matching observer type; cache snapshot must be complete for selected region/read_ts because data CF reads trust it.

Test signals: iterator test confirms cache-backed iteration after mirrored write.
