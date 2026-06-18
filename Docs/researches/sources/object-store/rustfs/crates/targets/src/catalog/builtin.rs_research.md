# sources/object-store/rustfs/crates/targets/src/catalog/builtin.rs

## Purpose
Builds built-in audit and notification target descriptors for all supported channel target types. These descriptors connect config subsystem names, request validators, valid config keys, config validation functions, argument builders, and concrete target constructors.

## Important APIs and Functions
`build_descriptor` constructs a generic `BuiltinTargetDescriptor<E>` from subsystem metadata, request validator, target type string, valid field list, validation callback, and target creation callback. `build_admin_descriptor` creates admin-facing descriptor metadata without instantiating targets.

`builtin_audit_target_admin_descriptors` and `builtin_notify_target_admin_descriptors` return descriptor metadata for AMQP, webhook, MQTT, NATS, Pulsar, Kafka, Redis, MySQL, and PostgreSQL. `builtin_audit_target_descriptors<E>` and `builtin_notify_target_descriptors<E>` return full descriptors that validate config and construct typed targets such as `AMQPTarget`, `WebhookTarget`, `MQTTTarget`, `NATSTarget`, `PulsarTarget`, `KafkaTarget`, `RedisTarget`, `MySqlTarget`, and `PostgresTarget`.

## Control Flow and State
All functions build vectors on demand. There is no registry mutation in this file. The descriptors capture closures that later validate configs and construct boxed target trait objects.

## Integration Points
This module joins `rustfs_config` audit/notify constants, `crate::config` validators/builders, `crate::plugin` descriptor types, `crate::target` concrete implementations, `TargetType`, and default queue directories (`AUDIT_DEFAULT_DIR`, `EVENT_DEFAULT_DIR`). It feeds both runtime target loading and extension catalog generation.

## Risks
The audit and notify descriptor lists are manually duplicated; missing one target in one list can cause inconsistent admin/runtime behavior. Generic event type `E` requires clone/serde bounds across all targets. Each closure encodes a default queue directory and target type, so copy-paste errors are plausible. The file has no local tests; uniqueness is partially checked by extension catalog tests that consume admin descriptors.

## Test Signals
No direct tests. Indirect signals come from catalog extension tests expecting nine unique built-in target extension schemas and from target-specific config/integration tests elsewhere.
