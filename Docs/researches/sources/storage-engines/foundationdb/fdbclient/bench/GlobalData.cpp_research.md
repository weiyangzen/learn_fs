# sources/storage-engines/foundationdb/fdbclient/bench/GlobalData.cpp

Purpose: shared benchmark data provider for stable key/value buffers.

Important APIs and control flow: `initGlobalData` lazily allocates a 1 MiB buffer with `allocateFast` and refreshes it with deterministic random bytes each call. `getKV` returns a `KeyValueRef` over the first `keySize` bytes and following `valueSize` bytes. `getKey` returns a `KeyRef` of requested size.

State and persistence: `globalData` is process-global heap memory. It is never freed in this file, matching benchmark-process lifetime assumptions. No durable persistence.

Dependencies and integration: includes `FDBTypes.h`, local `GlobalData.h`, and `IRandom.h`; used by mutation list benchmarks.

Risks: returned refs alias global memory that is overwritten by subsequent `initGlobalData` calls. Callers must not assume contents survive another `getKV`/`getKey` call if contents matter. Assertions enforce max total size and nonzero key size.

Test signals: indirectly validated by benchmarks that consume `getKV` and `getKey`.
