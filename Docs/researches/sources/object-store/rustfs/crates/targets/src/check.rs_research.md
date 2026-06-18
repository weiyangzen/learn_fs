# sources/object-store/rustfs/crates/targets/src/check.rs

## Purpose
Connectivity and preflight probe module for RustFS notification/audit targets. It exposes async checks for MQTT, NATS, Pulsar, MySQL, PostgreSQL, Kafka, Redis, and AMQP so admin validation and runtime initialization can confirm a target backend is reachable before or while enabling delivery.

## Important APIs, types, and functions
- `check_mqtt_broker_available` and `check_mqtt_broker_available_with_tls` parse a broker URL, build `rumqttc` options through the MQTT target helper, subscribe to a topic, and wait for an event-loop poll.
- `check_nats_server_available`, `check_pulsar_broker_available`, `check_redis_server_available`, and `check_amqp_broker_available` delegate to target-specific connection builders, then run lightweight liveness calls such as NATS `flush`, Pulsar topic lookup, Redis ping, or AMQP connection/channel status.
- `check_mysql_server_available` validates `MySqlArgs`, parses DSN details, builds a `mysql_async` pool with optional TLS material, and runs `SELECT 1`.
- `check_postgres_server_available` validates `PostgresArgs`, builds a pool, executes `SELECT 1`, and verifies table readability with `LIMIT 0`.
- `check_kafka_broker_available` validates `KafkaArgs`, maps acks to `RequiredAcks`, applies optional security config, and creates an async producer.

## Control flow
Every check performs local validation before network I/O when the target args support it. The network phase is bounded by `tokio::time::timeout` values of 3, 5, or 8 seconds depending on backend. Errors are mapped into `TargetError` variants: malformed configuration stays `Configuration`, unreachable brokers often become `Network` or `NotConnected`, and hung handshakes become `Timeout`.

## State and persistence behavior
The module does not persist application data. It opens short-lived client connections and deliberately avoids side-effecting operations beyond read-only probes and broker handshakes. MySQL intentionally relies on pool drop instead of `pool.disconnect()` because tests documented that disconnect can hang past the probe timeout.

## Dependencies and integration points
This file integrates the public target validation surface with backend crates: `rumqttc`, `async_nats`, Pulsar helpers, `mysql_async`, PostgreSQL pool helpers, `rustfs_kafka_async`, Redis helpers, and AMQP helpers. The functions are re-exported from `lib.rs` for callers outside the crate.

## Risks and edge cases
The checks can produce false negatives in slow DNS/TLS environments because timeouts are short and fixed. Kafka only validates producer creation, not topic existence. MQTT only waits for one event after subscribe, so broker-specific auth or ACL behavior can affect the signal. MySQL and PostgreSQL TLS paths are passed through backend-specific builders, so path validation must remain aligned with `target_args.rs` and the target modules.

## Test signals
Unit tests assert that Kafka SASL without TLS, invalid MySQL table identifiers, and unpaired MySQL TLS client fields fail before opening network connections. These tests focus on fast local validation and guard against accidental probe behavior that reaches the network for invalid configs.
