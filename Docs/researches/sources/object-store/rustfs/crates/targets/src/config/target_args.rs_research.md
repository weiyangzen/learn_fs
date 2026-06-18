# sources/object-store/rustfs/crates/targets/src/config/target_args.rs

## Purpose
Transforms merged `KVS` configuration into strongly typed target argument structs and validates backend-specific configuration rules. It is the main compatibility layer between RustFS legacy config keys and runtime target constructors.

## Important APIs, types, and functions
- Builders: `build_amqp_args`, `build_webhook_args`, `build_mqtt_args`, `build_nats_args`, `build_pulsar_args`, `build_redis_args`, `build_postgres_args`, `build_kafka_args`, and `build_mysql_args`.
- Validators: `validate_*_config` wrappers either build and discard args or run stricter preflight checks.
- Internal parsers include `parse_kafka_acks_value`, `parse_kafka_sasl_enable`, and `parse_amqp_bool_value`.
- Backend args include target type so the same builder path can support notify and audit domains where target implementations allow both.

## Control flow
Each builder reads required keys, applies defaults for optional keys, parses URLs or DSNs, maps booleans/durations/limits, constructs the backend args struct, and usually calls its `validate()` method. Validators are thin wrappers except where extra rules are needed, such as webhook client cert/key pairing and queue-dir absoluteness or MQTT QoS/queue compatibility.

## State and persistence behavior
The module does not persist state. It decides queue directories and queue limits that downstream targets use for durable delivery stores. It enforces absolute queue/TLS path rules before those downstream components open files.

## Dependencies and integration points
It depends heavily on `rustfs_config` key constants, target modules for argument structs and validators, `rumqttc::QoS`, URL parsing from `common.rs`, and `TargetError`. `plugin.rs` descriptors use these validators and builders when registered target plugins are created from config.

## Risks and edge cases
Some numeric options silently fall back when parsing fails, while others, such as MySQL `max_open_connections`, return errors; callers need to know which fields are strict. Kafka infers SASL enablement from credentials unless explicitly disabled, which is convenient but subtle. MQTT build maps invalid QoS values to `AtLeastOnce`, while validation rejects invalid QoS, so callers should validate before relying on built args.

## Test signals
The large unit suite covers AMQP schemes, booleans, credentials, TLS path pairing, Kafka acks/SASL/TLS interactions, MySQL DSN/table/TLS/queue/max-connection validation, Redis defaults and tuning fields, and PostgreSQL DSN/table/format/TLS/queue rules.
