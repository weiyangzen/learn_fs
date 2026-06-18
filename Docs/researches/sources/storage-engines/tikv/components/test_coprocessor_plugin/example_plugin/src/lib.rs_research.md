# sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/src/lib.rs

## Purpose
This is the minimal dynamic plugin implementation for coprocessor plugin tests. It proves that the plugin API macro and trait can produce a loadable plugin library.

## Important APIs, Types, And Functions
`ExamplePlugin` is an empty `Default` type implementing `CoprocessorPlugin`. Its `on_raw_coprocessor_request` method has the expected API shape: ranges, raw request, raw storage, and `PluginResult<RawResponse>`. The implementation is `unimplemented!()`. `declare_plugin!(ExamplePlugin)` emits the plugin registration/export required by the plugin runtime.

## Control Flow, State, And Integration Points
There is no runtime state. Control reaches the plugin only if a raw coprocessor request is dispatched to it; at that point it panics because the example is intentionally not functional. It integrates solely with `coprocessor_plugin_api` and Rust's dynamic-library build mode from the manifest.

## Risks And Test Signals
The unimplemented method means this plugin should be used for loading/registration tests, not request-processing behavior. Any test that invokes the raw request hook should expect a panic or update this implementation. Build and plugin discovery are the primary signals.
