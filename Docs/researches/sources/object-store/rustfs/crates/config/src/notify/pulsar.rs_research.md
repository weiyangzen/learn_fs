<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/pulsar.rs -->
# sources/object-store/rustfs/crates/config/src/notify/pulsar.rs

## Purpose
Registers Pulsar notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_PULSAR_KEYS` includes broker, topic, auth token, username/password, TLS CA/allow-insecure/hostname verification, queue dir/limit, enable/comment. `ENV_NOTIFY_PULSAR_KEYS` maps to `RUSTFS_NOTIFY_PULSAR_*`.

## Control flow
No local logic; Pulsar target parsing uses these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/pulsar.rs -->
