# sources/storage-engines/tikv/components/engine_traits/src/write_batch.rs

Purpose: Defines generic write-batch creation, mutable batch commands, and batch commit semantics.

Important APIs and control flow: `WriteBatchExt` associates an engine write-batch type, exposes `WRITE_BATCH_MAX_KEYS`, and creates batches with optional capacity. `Mutable` defines put/delete/range-delete operations plus protobuf helpers. `WriteBatch` extends `Mutable` with option-aware writes, write callbacks, default writes, data size, count, emptiness, threshold checks, clear, save-point push/pop/rollback, and merge.

State, persistence, and dependencies: Implementations buffer commands in memory until `write_opt` persists them atomically or backend-specifically. Save points are in-memory rollback markers.

Integration points, risks, and test signals: Used by raft apply, transactions, and batched mutation paths. Risks include atomicity differences across implementations, unclear consequences of exceeding max keys, save-point stack errors, range-delete semantics, callback sequence counts, and merge ownership. Shared tests exercise writes across direct and batch APIs; TiRocks tests cover thresholds and merges.
