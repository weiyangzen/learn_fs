# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/storage_api.rs

Purpose: defines low-level async storage operations exposed to coprocessor plugins.

Important APIs and types: aliases `Key`, `Value`, `KvPair`, and the `RawStorage` trait with `get`, `batch_get`, `scan`, `put`, `batch_put`, `delete`, `batch_delete`, and `delete_range`.

Control flow: plugin code calls these async methods to access the current node’s raw storage. Range methods use half-open `[start, end)` semantics. Batch methods are recommended for performance.

State and persistence: trait implementers perform real storage reads/writes/deletes; this API file stores no state itself.

Dependencies and integration: uses `async_trait(?Send)` to allow non-`Send` async futures, and `PluginResult` for infrastructure errors. It is consumed by `CoprocessorPlugin::on_raw_coprocessor_request`.

Risks: raw byte keys/values and range boundaries place correctness on plugin authors. Region errors are reported through `PluginError::KeyNotInRegion`, but callers must still choose ranges that match placement constraints. Non-`Send` async methods constrain executor integration.

Test signals: no direct tests in this file; behavior depends on TiKV’s host-side `RawStorage` implementation and plugin integration tests.
