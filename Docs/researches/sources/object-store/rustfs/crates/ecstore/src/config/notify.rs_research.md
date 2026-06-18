# sources/object-store/rustfs/crates/ecstore/src/config/notify.rs

## Purpose
This file defines default notification target KVS for every supported event sink. It is data scaffolding for admin config registration and server-config JSON conversion.

## Important APIs, types, and functions
Exported statics are `DEFAULT_NOTIFY_WEBHOOK_KVS`, `DEFAULT_NOTIFY_MQTT_KVS`, `DEFAULT_NOTIFY_AMQP_KVS`, `DEFAULT_NOTIFY_NATS_KVS`, `DEFAULT_NOTIFY_PULSAR_KVS`, `DEFAULT_NOTIFY_REDIS_KVS`, `DEFAULT_NOTIFY_POSTGRES_KVS`, `DEFAULT_NOTIFY_KAFKA_KVS`, and `DEFAULT_NOTIFY_MYSQL_KVS`. Each is a `LazyLock<KVS>` of `KV` entries.

## Control flow
The only runtime behavior is lazy initialization. `config::init` registers these under `NOTIFY_*_SUB_SYS`, and `config/com.rs` uses them to merge defaults, decode external `notify` JSON, and render only differences from defaults.

## State and persistence behavior
The statics are immutable. Persisted state is managed in server config elsewhere. Defaults include disabled enable flags, queue directories/limits, TLS and credential keys, and backend-specific defaults such as AMQP persistence, Kafka acks, Redis channel, and MySQL table.

## Dependencies and integration points
It depends on constants from `rustfs_config` and `rustfs_config::notify`. Event notification client setup, admin config rendering, and config migration rely on these key names and defaults.

## Risks and edge cases
This file is effectively a schema contract. Changing keys, defaults, or `hidden_if_empty` can break compatibility or runtime behavior. Empty secrets are hidden, but non-empty secrets remain config data. There is no validation here; malformed values fail only in downstream client setup.

## Test signals
No local tests. `config/com.rs` indirectly covers webhook, MQTT, Kafka, AMQP, and MySQL notify conversion, but not NATS, Pulsar, Redis, or Postgres defaults.
