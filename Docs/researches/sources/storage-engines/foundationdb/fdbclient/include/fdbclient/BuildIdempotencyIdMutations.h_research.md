# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BuildIdempotencyIdMutations.h

Purpose: template helper for building idempotency-ID key/value mutations for committed transaction batches.

Important APIs and control flow: `buildIdempotencyIdMutations` accepts commit transaction requests, an `IdempotencyIdKVBuilder`, commit version, committed-status vector, target committed value, a locked flag, and an `onKvReady` callback. It sets the commit version, walks transactions in chunks of 256, filters to committed transactions that are lock-aware if required, adds valid idempotency IDs with their batch index, then emits any builder output via callback and clears the builder each chunk.

State and persistence: function itself is stateless except for mutating the builder. Emitted `KeyValue`s become commit metadata used to make retries idempotent.

Dependencies and integration: depends on `CommitProxyInterface.h` for `CommitTransactionRequest` and `IdempotencyId.h` for builder/id refs. Used by commit proxy paths and benchmarked in `BenchIdempotencyIds.cpp`.

Risks: `committed` must be at least as large as `trs`; no explicit bounds check exists. Chunking at 256 likely matches batch-index encoding and must remain consistent with builder expectations. Lock-aware filtering is critical when database locking is active.

Test signals: commit idempotency tests and the dedicated benchmark.
