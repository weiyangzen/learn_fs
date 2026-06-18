# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/lib.rs

Purpose: crate root and user-facing documentation for writing TiKV custom coprocessor plugins.

Important APIs and types: exposes hidden `allocator` and `util` modules for generated macro use, declares private `errors`, `plugin_api`, and `storage_api` modules, and re-exports `PluginError`, `PluginResult`, `CoprocessorPlugin`, raw request/response aliases, `RawStorage`, and storage key/value aliases.

Control flow: no runtime flow. The doc example shows implementing `CoprocessorPlugin` and invoking `declare_plugin!`.

State and persistence: none directly.

Dependencies and integration: establishes the public API consumed by plugin crates compiled as `dylib`. Documentation emphasizes `dylib` rather than `cdylib`/`staticlib` so plugins can use TiKV’s allocator.

Risks: public API stability is ABI-sensitive because plugins are dynamically loaded. Hidden modules are still public for macro expansion, so changing them can break downstream plugin builds. The example in docs must stay aligned with trait signatures.

Test signals: doc example is marked `no_run`; no direct runtime tests here.
