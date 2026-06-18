# sources/object-store/rustfs/crates/ecstore/src/config/audit.rs

## Purpose
Defines default key/value configuration sets for RustFS audit log targets: webhook, MQTT, AMQP, NATS, Pulsar, Redis, Postgres, Kafka, and MySQL.

## Important APIs, types, and functions
Public `LazyLock<KVS>` statics include `DEFAULT_AUDIT_WEBHOOK_KVS`, `DEFAULT_AUDIT_MQTT_KVS`, `DEFAULT_AUDIT_AMQP_KVS`, `DEFAULT_AUDIT_NATS_KVS`, `DEFAULT_AUDIT_PULSAR_KVS`, `DEFAULT_AUDIT_REDIS_KVS`, `DEFAULT_AUDIT_POSTGRES_KVS`, `DEFAULT_AUDIT_KAFKA_KVS`, and `DEFAULT_AUDIT_MYSQL_KVS`. Each contains `KV` entries with key, default value, and `hidden_if_empty`.

## Control flow
There is no dynamic control flow beyond lazy initialization. Each target starts disabled and supplies endpoint/broker/table/topic credentials, TLS settings, queue directory/limit, retry or timeout settings, format settings, and comments as appropriate.

## State and persistence behavior
The statics provide immutable defaults used by configuration loading/merging. Actual persisted server configuration lives in the broader `rustfs_config` subsystem, not here. Sensitive fields are marked hidden when empty for config display behavior.

## Dependencies and integration points
This file depends heavily on audit/server config constants from `rustfs_config`, `KV/KVS`, `EnableState`, default limits, event queue directory defaults, and Redis default channel. It is an integration source for admin/config APIs that enumerate available audit targets and defaults.

## Risks and edge cases
There are apparent duplicated struct fields in the source around AMQP client cert and Postgres TLS required entries, which should be checked at compile time. Defaults vary in units (`Redis keep alive` is `"15"` while others use duration strings). Incorrect `hidden_if_empty` flags could expose secrets or hide useful settings.

## Test signals
No local tests are present. Good coverage would assert every default KVS contains `enable` and `comment`, sensitive fields are hidden, queue defaults are consistent, and each target-specific required key is present exactly once.
