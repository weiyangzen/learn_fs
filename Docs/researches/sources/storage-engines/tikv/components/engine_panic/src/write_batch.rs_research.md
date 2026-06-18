# sources/storage-engines/tikv/components/engine_panic/src/write_batch.rs

Purpose: Panic skeleton for write-batch creation, mutation, savepoints, merging, and write execution.

Important APIs and types: `PanicEngine` implements `WriteBatchExt` with associated `PanicWriteBatch` and `WRITE_BATCH_MAX_KEYS = 1`. `PanicWriteBatch` implements `WriteBatch` and `Mutable`.

Control flow and state: All methods panic, including write, size/count inspection, clear, savepoint operations, merge, put/delete, and range delete. There is no batch state.

Dependencies and integration: Used as the associated write batch for both KV and raft panic-engine traits.

Risks: Runtime use panics; `WRITE_BATCH_MAX_KEYS` is a placeholder and not a functional capacity limit.

Test signals: No tests.
