# sources/storage-engines/tikv/src/coprocessor_v2/config.rs

## Purpose
Defines configuration for the v2 plugin-based coprocessor framework.

## Important APIs, Types, and Functions
`Config` is `Clone`, `Debug`, `Serialize`, `Deserialize`, `PartialEq`, and `Default`. Its only field is `coprocessor_plugin_directory: Option<PathBuf>`, deserialized with serde defaults and kebab-case names.

## Control Flow
No runtime control flow exists here. `Endpoint::new` consumes this config and starts plugin hot reloading only when the directory is present.

## State and Persistence Behavior
The config itself is in-memory after deserialization. It controls persistent filesystem interaction indirectly by selecting a plugin directory for dynamic libraries.

## Dependencies and Integration Points
Uses `serde_derive` macros from the crate root and standard `PathBuf`. Integrated by `coprocessor_v2::Endpoint` and the broader TiKV config system.

## Risks and Edge Cases
An absent directory disables coprocessor plugins. A configured directory causes TiKV to create/watch/load dynamic libraries from that path, so config validation and operational permissions matter.

## Test Signals
No direct tests. Behavior is indirectly covered by endpoint and plugin registry tests.
