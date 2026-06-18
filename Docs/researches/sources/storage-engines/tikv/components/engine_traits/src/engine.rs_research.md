# sources/storage-engines/tikv/components/engine_traits/src/engine.rs

Purpose: Defines `KvEngine`, the central generic key-value storage engine trait for TiKV.

Important APIs and control flow: `KvEngine` composes read, write, iteration, options, import, SST, compaction, range/MVCC/TTL/table properties, performance, misc, and checkpoint traits. It associates a `Snapshot`, creates snapshots, syncs writes to disk, flushes metrics through `StatisticsReporter`, exposes a temporary `bad_downcast`, and has a default `can_apply_snapshot` hook.

State, persistence, and dependencies: Implementors own persistent KV state, CF metadata, snapshots, write batches, options, and metrics. The trait expresses what TiKV needs but holds no state itself.

Integration points, risks, and test signals: This is the primary type bound throughout TiKV. Risks include an overly broad trait forcing all engines to implement every feature, concrete downcast leakage, snapshot apply hooks being backend-specific, and associated-type coupling. Shared tests instantiate `KvTestEngine` through this trait and validate core read/write/snapshot/iterator/SST behavior.
