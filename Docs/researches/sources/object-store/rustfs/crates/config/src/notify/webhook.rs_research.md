<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/webhook.rs -->
# sources/object-store/rustfs/crates/config/src/notify/webhook.rs

## Purpose
Registers webhook notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_WEBHOOK_KEYS` includes endpoint, auth token, queue limit/dir, client cert/key/CA, skip TLS verify, enable/comment. `ENV_NOTIFY_WEBHOOK_KEYS` maps to `RUSTFS_NOTIFY_WEBHOOK_*`.

## Control flow
No local logic; webhook target parsing and HTTP client setup consume the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
Webhook auth token and client key are sensitive and must be redacted by downstream config display. `skip_tls_verify` is security-sensitive.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/webhook.rs -->
