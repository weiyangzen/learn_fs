# sources/object-store/rustfs/crates/s3select-api/src/query/session.rs

## Purpose
This file builds the DataFusion session state used by S3 Select queries. It registers an object store for the target bucket and provides an in-memory test store with CSV, JSON, and parquet fixtures.

## Important APIs, Types, And Functions
`SessionCtx` wraps a DataFusion `SessionState` and exposes `inner()`. `SessionCtxFactory` has `is_test` and `create_session_ctx`. `build_df_session_context` constructs a runtime environment, default DataFusion features, and an object store for `s3://<bucket>`. Test mode uses `build_in_mem_store`; production mode uses `EcObjectStore::new`. Fixture helpers include `test_parquet_bytes` and `test_parquet_batch`.

## Control Flow
Session creation parses a bucket URL, builds `RuntimeEnv`, creates `SessionStateBuilder`, registers either `InMemory` or `EcObjectStore` under that URL, and returns the session state. Test store population writes `test.csv`, `test.json`, `test.jsonl`, and `test.parquet` into memory; errors are logged but the store is still returned.

## State And Persistence Behavior
Session state is per query and in memory. Production sessions reference the shared global `ECStore` through `EcObjectStore`. Test mode persists fixture bytes only in the `InMemory` object store for that session.

## Dependencies And Integration Points
It integrates DataFusion session/runtime APIs, object_store registration, Arrow/parquet writer APIs, `s3s` request context, and the `EcObjectStore` adapter. `SimpleQueryDispatcher` obtains sessions through this factory.

## Risks And Edge Cases
`Url::parse` unwraps the constructed bucket URL. Test store fixture writes log errors instead of failing session creation, so broken fixtures may surface later as schema/read errors. Production session creation depends on the global `ECStore` being initialized. Fixture names must match test input keys and listing extensions.

## Test Signals
The file embeds fixture-generation code rather than unit tests. Query crate integration tests rely on test sessions for CSV, JSON DOCUMENT, JSON LINES, parquet, scan-range, and concurrent query coverage.
