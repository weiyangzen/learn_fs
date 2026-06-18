<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mysql.rs -->
# sources/object-store/rustfs/crates/config/src/notify/mysql.rs

## Purpose
Registers MySQL notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_MYSQL_KEYS` includes DSN string, table, format, TLS CA/client cert/key, queue dir/limit, max open connections, enable/comment. `ENV_NOTIFY_MYSQL_KEYS` maps to `RUSTFS_NOTIFY_MYSQL_*`.

## Control flow
No local logic; database target setup uses these names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mysql.rs -->
