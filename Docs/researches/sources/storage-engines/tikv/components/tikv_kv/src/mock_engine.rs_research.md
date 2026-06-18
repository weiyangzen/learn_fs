# sources/storage-engines/tikv/components/tikv_kv/src/mock_engine.rs

Purpose: provides `MockEngine`, a testing wrapper around `RocksEngine` that records writes, validates expected modifies, and can run a hook before async snapshots.

Important APIs: `MockEngine::take_last_modifies()` drains observed write batches; `rocks_engine()` exposes the underlying Rocks engine. `ExpectedWrite` is a builder-style expectation for a specific `Modify` and expected proposed/committed subscription behavior. `MockEngineBuilder` constructs wrappers from an existing `RocksEngine`, appends expectations, and registers a `pre_async_snapshot` closure.

Control flow: `MockEngine` implements `Engine` mostly by delegation. `async_write()` checks the pending expectation list against every `Modify` in the batch and the subscribed event flags, records a clone of `batch.modifies`, then delegates to `base.async_write()`. `async_snapshot()` invokes the optional pre-snapshot hook before forwarding to Rocks.

State and persistence: persistent data lives in the wrapped RocksDB engine. Mock-only state is shared through `Arc<Mutex<...>>`: a linked list of expected writes, a vector of last modifies, and an optional snapshot hook. `ExpectedWriteList::drop()` asserts all expectations were consumed, allowing cloned `MockEngine`s to share a single assertion lifecycle.

Dependencies and integration: depends on the public `tikv_kv` `Engine`, `Modify`, `WriteData`, `WriteEvent`, `RocksEngine`, and KV protobuf `Context`. It is intended for unit/integration tests that need realistic engine behavior plus verification of write paths.

Risks: expectation checking panics on mismatch or unexpected writes; clones share expectations, so concurrent tests must order writes deterministically. `take_last_modifies()` drains global mock state. Callback assertions only inspect subscription flags, not whether the downstream stream is polled.

Test signals: this file has no tests, but it is itself test infrastructure; correctness is exercised by tests that use `MockEngineBuilder` expectations.
