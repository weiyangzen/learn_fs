# sources/object-store/rustfs/crates/config/src/audit/mod.rs

## Purpose
Aggregates audit configuration modules, re-exports their constants, and defines audit subsystem identifiers.

## Important APIs, types, and functions
Declares submodules for AMQP, Kafka, MQTT, MySQL, NATS, Postgres, Pulsar, Redis, and Webhook. Exports `AUDIT_PREFIX`, `AUDIT_ROUTE_PREFIX`, subsystem names, `AUDIT_REDIS_DEFAULT_CHANNEL`, `AUDIT_STORE_EXTENSION`, and `AUDIT_SUB_SYSTEMS`.

## Control flow
There is no runtime control flow. Compile-time module inclusion plus public re-exports create the audit configuration namespace.

## State and persistence behavior
All values are static constants. `AUDIT_ROUTE_PREFIX` is built at compile time with `const_str::concat!`.

## Dependencies and integration points
Uses `crate::DEFAULT_DELIMITER` and all target modules. Config routing, subsystem validation, and audit target discovery consume `AUDIT_SUB_SYSTEMS`.

## Risks and edge cases
Adding a new audit target requires updating module declarations, re-exports, subsystem constants, and `AUDIT_SUB_SYSTEMS`. The Redis default channel lives in the aggregate module, so Redis target code must import from here or duplicate it.

## Test signals
No local tests; compile-time module checks and audit config integration tests are the expected signals.
