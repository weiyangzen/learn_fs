# sources/storage-engines/tikv/src/coprocessor_v2/raw_storage_impl.rs

## Purpose
Adapts TiKV `Storage` into the `coprocessor_plugin_api::RawStorage` trait exposed to v2 coprocessor plugins.

## Important APIs, Types, and Functions
`RawStorageImpl<'a, E, L, F>` stores a per-request `Context` and borrowed `Storage`. It implements async raw operations: `get`, `batch_get`, `scan`, `put`, `batch_put`, `delete`, `batch_delete`, and `delete_range`. `PluginErrorShim` converts TiKV storage errors and canceled callbacks into plugin errors.

## Control Flow
Read operations clone the request context, call storage raw read methods with an empty column family string, await the result, and convert kv pairs using `extract_kv_pairs`. Mutations create a paired callback/future, invoke the storage raw write API, then await callback completion and map both synchronous and callback errors. `scan` uses `usize::MAX` as limit, `key_only=false`, and forward order.

## State and Persistence Behavior
The adapter does not own persistent state. Mutating methods persist data through TiKV raw storage. It clones context per call to preserve request region/API metadata.

## Dependencies and Integration Points
Depends on `api_version::KvFormat`, `async_trait`, plugin API types, `kvproto::Context`, TiKV `Storage`, and lock manager traits. It is created by `Endpoint::handle_request_impl` for each plugin request.

## Risks and Edge Cases
`scan` can request an unbounded range with `usize::MAX`, so plugin-controlled ranges can be expensive. All operations use an empty CF string, which relies on storage raw API defaults. Error mapping only special-cases key-not-in-region and timeout; other storage errors are wrapped in `PluginError::Other` with a boxed `storage::Result<()>`, which endpoint later inspects for region errors.

## Test Signals
Async tests cover put/get/overwrite/delete, batch put/get/delete, scan ordering, missing keys, and delete range under API v2 test storage. Tests do not cover timeout, region errors, cancellation, large scans, or non-default CF behavior.
