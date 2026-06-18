<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/store.rs -->
# sources/object-store/rustfs/crates/config/src/notify/store.rs

## Purpose
Defines queue-store file suffix constants for notification events.

## Important APIs, types, and functions
`DEFAULT_EXT` is `.unknown`, `COMPRESS_EXT` is `.snappy`, and `NOTIFY_STORE_EXTENSION` is `.event`.

## Control flow
No local logic; event queue store code chooses extensions from these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
Extension changes can break compatibility with existing queue files and compression detection.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/store.rs -->
