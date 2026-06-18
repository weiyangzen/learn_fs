# sources/storage-engines/tikv/components/online_config/Cargo.toml

## Purpose
This manifest defines `online_config`, the runtime trait and value crate for TiKV online configuration updates.

## Important APIs, Types, and Functions
Runtime dependencies are `chrono`, the local `online_config_derive` proc macro, and `serde`; tests use `toml`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no state, but the crate supports mutable runtime configuration state in consumers.

## Dependencies and Integration Points
`chrono` supports schedule/time config values; `serde` supports encoder output for config serialization; `online_config_derive` generates trait implementations.

## Risks
The crate exports the derive macro, so manifest path/version changes can break many config structs. Serialization compatibility matters for config files and admin tooling.

## Test Signals
Tests are in `src/lib.rs` and cover generated online config behavior.
