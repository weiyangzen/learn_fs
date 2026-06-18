# sources/storage-engines/tikv/components/test_coprocessor_plugin/example_plugin/Cargo.toml

## Purpose
This manifest defines `example_coprocessor_plugin`, a private dynamic-library example for the coprocessor plugin API.

## Dependencies And Integration Points
The `[lib]` section sets `crate-type = ["dylib"]`, which is required for runtime plugin loading rather than normal static Rust linkage. Its only dependency is the workspace `coprocessor_plugin_api`, making it a minimal compatibility fixture.

## State, Persistence, And Risks
There is no manifest-level state or persistence. The main risk is ABI/API compatibility: because this crate builds as a dynamic library, changes in plugin declaration, exported symbols, or the plugin API surface should be caught by compiling/loading this example.

## Test Signals
Successful build proves the example can link against `coprocessor_plugin_api` as a dynamic plugin. Runtime tests must still verify that the exported plugin declaration loads as expected.
