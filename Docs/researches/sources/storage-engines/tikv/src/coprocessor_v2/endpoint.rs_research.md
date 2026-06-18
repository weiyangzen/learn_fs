# sources/storage-engines/tikv/src/coprocessor_v2/endpoint.rs

## Purpose
Provides the request endpoint for the plugin-based raw coprocessor framework. It dispatches `RawCoprocessorRequest` messages to dynamically loaded plugins and translates plugin/storage failures into protobuf responses.

## Important APIs, Types, and Functions
`Endpoint` holds an optional `Arc<PluginRegistry>`. `Endpoint::new` initializes the registry and starts hot reloading if a plugin directory is configured. `handle_request` returns a ready future containing `RawCoprocessorResponse`. `handle_request_impl` validates plugin availability, plugin name, semver constraint, constructs `RawStorageImpl`, converts request ranges to Rust ranges, and invokes `plugin.on_raw_coprocessor_request`. `extract_region_error` recovers region errors wrapped inside plugin `Other` errors.

## Control Flow
Requests are synchronously evaluated into a result, then wrapped in `std::future::ready`. Disabled plugin support returns a response error. Missing plugin names and semver parse/mismatch failures become string errors. Plugin errors that contain storage region errors are promoted to `region_error`; other plugin failures become response `error`.

## State and Persistence Behavior
Endpoint state is the shared plugin registry. Request handling does not mutate endpoint state but plugins may mutate raw storage through `RawStorageImpl` methods. Response data is plugin-provided opaque bytes.

## Dependencies and Integration Points
Depends on `coprocessor_plugin_api`, `kvproto::kvrpcpb`, `semver`, v2 config/registry/raw storage modules, and TiKV `Storage`. It is the service boundary between RPC handling and plugin code.

## Risks and Edge Cases
Plugin calls run in-process and can perform arbitrary plugin logic. Version constraints are request-controlled and must parse under semver. The future is ready, so any plugin work performed before returning can block the caller's execution context. Region-error extraction depends on plugin errors preserving the storage result in the expected `Any` payload.

## Test Signals
No direct tests in this file. Plugin registry and raw storage adapters have their own tests, but endpoint dispatch/version/error paths appear lightly covered.
