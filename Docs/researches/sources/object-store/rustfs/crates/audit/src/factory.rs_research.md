# sources/object-store/rustfs/crates/audit/src/factory.rs

## Purpose

`factory.rs` exposes RustFS built-in audit target descriptors and plugin descriptors specialized for `AuditEntry` payloads.

## Important APIs and Types

`builtin_target_descriptors()` calls `rustfs_targets::catalog::builtin::builtin_audit_target_descriptors::<AuditEntry>()`. `builtin_target_plugins()` converts those descriptors into cloned `TargetPluginDescriptor<AuditEntry>` values.

## Control Flow

Runtime configuration loaders can call these functions to discover supported target types, validate fields, and create target instances. The file itself only maps catalog descriptors to plugin descriptors.

## State and Persistence

The file has no mutable state. Created target instances may persist queued messages or connect to external brokers depending on plugin configuration, but descriptor lookup itself is pure.

## Dependencies and Integration Points

It integrates with `rustfs-targets` built-in catalog descriptors and the audit crate's `AuditEntry` type. The tests use RustFS config constants and `ChannelTargetType` to validate AMQP plugin registration and target creation.

## Risks and Edge Cases

The factory relies on the target catalog to include all audit-capable targets. If the catalog changes field names or omits AMQP, tests should fail. `builtin_target_plugins` clones plugin descriptors; plugin descriptors must remain cheap and safe to clone. Misconfigured KVS values are validated by target plugin creation rather than this wrapper.

## Test Signals

Existing tests assert that an AMQP descriptor is present, exposes all configured AMQP keys, creates a target named `amqp`, preserves the configured id, and has no queue store when queue directory is empty. Broader coverage should check every built-in audit target type expected by the product.
