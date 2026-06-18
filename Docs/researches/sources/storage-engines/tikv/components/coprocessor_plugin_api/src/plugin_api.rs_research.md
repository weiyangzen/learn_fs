# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/plugin_api.rs

Purpose: defines the core trait implemented by a dynamically loaded coprocessor plugin.

Important APIs and types: `RawRequest = Vec<u8>`, `RawResponse = Vec<u8>`, and `CoprocessorPlugin: Send + Sync` with `on_raw_coprocessor_request`.

Control flow: TiKV calls `on_raw_coprocessor_request` with key ranges, raw request bytes, and a `RawStorage` handle. The plugin decodes the request, performs storage operations, and returns encoded response bytes or `PluginError`.

State and persistence: the trait itself stores no state. Plugin implementations may keep state in their struct and can use `Drop` for teardown, as noted in docs.

Dependencies and integration: depends on `storage_api::RawStorage`, `Key`, and `PluginResult`. Dynamic plugin construction is handled by `declare_plugin!` in `util.rs`, which returns a `Box<dyn CoprocessorPlugin>` as a raw trait-object pointer.

Risks: request and response formats are fully plugin-defined, so TiKV cannot validate semantic compatibility. The trait is `Send + Sync`, but storage methods use non-`Send` async_trait, so implementers must be careful about where futures are driven.

Test signals: no direct tests; ABI and trait compatibility are validated through plugin loading/build integration.
