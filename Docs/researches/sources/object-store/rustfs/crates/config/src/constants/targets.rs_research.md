<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/targets.rs -->
# sources/object-store/rustfs/crates/config/src/constants/targets.rs

## Purpose
Defines common notify/audit target KVS field names across webhook, MQTT, Kafka, AMQP, NATS, Pulsar, MySQL, Redis, and Postgres plus queue-store compression defaults.

## Important APIs, types, and functions
Field constants cover endpoints, credentials, TLS material, queue dir/limit, retry/timeouts, topics/subjects/channels, broker/address/DSN/table/format, SASL, Redis retry and timeout knobs, and `BASE_DSN_STRING`. `ENV_TARGET_STORE_COMPRESS` defaults queue-store compression to enabled.

## Control flow
No local flow; provider-specific notify modules assemble valid-key and env-key arrays from these names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with notify/audit target config parsing, persistent event queues, provider clients, TLS loaders, database writers, and queue-store compression.

## Risks and edge cases
These field names are persistent config contract. Renaming breaks stored configuration and environment mapping. Queue compression defaults to on, so readers/writers must agree on `.snappy` handling and migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Provider config tests should validate every key maps to the expected env var and persisted KVS field, especially TLS and queue compression settings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/targets.rs -->
