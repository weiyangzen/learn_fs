# sources/storage-engines/foundationdb/fdbclient/bench/BenchIdempotencyIds.cpp

Purpose: Google Benchmark workload for `buildIdempotencyIdMutations`, measuring commit-proxy idempotency key/value construction across transaction counts and id sizes.

Important APIs and control flow: `bench_add_idempotency_ids` allocates `CommitTransactionRequest` objects, optionally assigns random `IdempotencyIdRef`s, randomly marks transactions committed, then repeatedly calls `buildIdempotencyIdMutations`. The callback only prevents optimization. `getRuntimeFalse()` makes the `locked` flag opaque to the compiler while always false in practice.

State and persistence: benchmark state is transient. The generated idempotency KVs model persisted commit metadata, but this benchmark does not write to the database.

Dependencies and integration: includes Google Benchmark and `fdbclient/BuildIdempotencyIdMutations.h`; relies on `deterministicRandom`, transaction arenas, commit version increments, and `IdempotencyIdKVBuilder`.

Risks: the locked path is effectively not measured because `locked` never becomes true. Random committed masks and random IDs introduce data-shape variation, though deterministic randomness keeps benchmark runs reproducible under the FDB benchmark runtime.

Test signals: registered with `ArgsProduct({CreateRange(1, 16384, 4), {0,16,255}})` and exports `TimePerTransaction`, giving performance coverage for no IDs, small IDs, and max-sized IDs over growing transaction batches.
