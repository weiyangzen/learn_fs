# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/errors.rs

Purpose: defines error and result types for plugin storage operations and request handling.

Important APIs and types: `PluginResult<T>` and `PluginError` variants `KeyNotInRegion`, `Timeout`, `Canceled`, and `Other(String, Box<dyn Any>)`.

Control flow: no complex flow. `Display` formats user-facing messages; `std::error::Error` is implemented for integration with ordinary Rust error handling.

State and persistence: no state. Errors carry contextual payloads, including region bounds for key-region mismatches and arbitrary boxed data for `Other`.

Dependencies and integration: used by `RawStorage` async methods and `CoprocessorPlugin::on_raw_coprocessor_request`. The `Key` alias comes from storage API re-exports.

Risks: `Other` stores `Box<dyn Any>` without `Send`/`Sync` constraints, which matches the non-`Send` storage trait but can limit cross-thread handling. Plugins are expected to encode business-logic errors into `RawResponse`; this enum is for infrastructure/storage failures.

Test signals: no direct tests; correctness is primarily API contract stability.
