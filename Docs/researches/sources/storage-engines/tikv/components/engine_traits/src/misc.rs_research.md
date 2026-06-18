# sources/storage-engines/tikv/components/engine_traits/src/misc.rs

Purpose: Holds miscellaneous engine operations not yet factored into narrower traits.

Important APIs and control flow: `DeleteStrategy` selects delete-files, delete-blobs, delete-by-key, delete-by-range, or delete-by-writer with ingestion options. `StatisticsReporter` abstracts metrics collection/flush. `RangeStats` summarizes entries, MVCC versions, rows, deletes, and computes redundant keys. `MiscExt` exposes flush operations, delete-ranges across CFs, memtable stats, ingestion slowdown checks, engine size, path, WAL sync, compaction/background-work controls, existence/lock checks, stats dumps, sequence numbers, SST sizes, key counts, range stats, stall state, active memtable stats, global flush counters, and disk engine access.

State, persistence, and dependencies: Operations touch memtables, SSTs, Titan blobs, WALs, compaction state, and filesystem paths. Dependencies include `KvEngine`, write options, CF names, flow-control factors, and `Range`.

Integration points, risks, and test signals: Used throughout TiKV maintenance, admin, metrics, and apply paths. Risks include broad trait coupling, delete strategy semantics with snapshots, ingestion during writes, stale size estimates, and backend-specific no-op behavior. Shared tests cover path and sync; broader coverage is backend/integration-level.
