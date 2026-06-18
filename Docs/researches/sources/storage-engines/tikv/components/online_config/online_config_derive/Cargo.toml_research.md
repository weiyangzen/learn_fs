# sources/storage-engines/tikv/components/online_config/online_config_derive/Cargo.toml

## Purpose
This manifest defines the `online_config_derive` proc-macro crate that generates `OnlineConfig` implementations.

## Important APIs, Types, and Functions
It marks the library as `proc-macro = true` and depends on `proc-macro2`, `quote`, and `syn` with `extra-traits` and `full`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
The crate is consumed by `online_config`, which re-exports the derive macro for TiKV config structs.

## Risks
Proc-macro dependency changes can alter generated syntax or compiler diagnostics. The derive assumes the runtime crate is named `online_config`, so renaming/re-exporting patterns are important.

## Test Signals
The generated code is tested through `online_config/src/lib.rs` tests.
