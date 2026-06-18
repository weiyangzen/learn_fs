<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mod.rs -->
# sources/object-store/rustfs/crates/config/src/notify/mod.rs

## Purpose
Aggregates notification target constants and defines shared notification subsystem identifiers and concurrency defaults.

## Important APIs, types, and functions
Re-exports provider modules for AMQP, ARN, Kafka, MQTT, MySQL, NATS, Postgres, Pulsar, Redis, store, and webhook. Defines `DEFAULT_TARGET`, `NOTIFY_PREFIX`, `NOTIFY_ROUTE_PREFIX`, target stream/send concurrency env keys and defaults, subsystem list `NOTIFY_SUB_SYSTEMS`, provider subsystem names, and default Redis channel.

## Control flow
Rust module imports and `pub use` expose provider constants. `NOTIFY_ROUTE_PREFIX` is computed at compile time from `notify` plus the default delimiter.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with event notification routing, admin config subsystem registration, target stream fan-out, provider clients, and persisted notification target names.

## Risks and edge cases
Subsystem names are persistent config/API contract. Concurrency defaults affect throughput and downstream pressure. Dead-code subsystem constants for NSQ/Elasticsearch signal legacy or planned providers and must not be accidentally exposed as supported without implementation.

## Test signals
Tests should validate provider subsystem registration, route prefix construction, concurrency env parsing, and that every listed subsystem has matching key/env arrays.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mod.rs -->
