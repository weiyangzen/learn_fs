# sources/object-store/rustfs/crates/notify/src/factory.rs

## Purpose
Exposes built-in notification target plugin descriptors for the notify crate.

## Important APIs, types, and functions
- `builtin_target_descriptors` returns `BuiltinTargetDescriptor<Event>` values from `rustfs_targets::catalog::builtin::builtin_notify_target_descriptors`.
- `builtin_target_plugins` maps descriptors into cloneable `TargetPluginDescriptor<Event>` values.

## Control flow
The module delegates descriptor construction to `rustfs_targets`, then maps descriptors to plugin descriptors for registration in `TargetRegistry::new`.

## State and persistence behavior
No state is stored and no config is persisted. Target instances created from these descriptors may later have stores/replay behavior depending on target type and KVS config.

## Dependencies and integration points
Links the notify crate's concrete `Event` payload type to the generic target plugin catalog. Used by `registry.rs`.

## Risks and edge cases
Plugin availability and valid fields are defined outside this crate. Any mismatch between `rustfs_config::notify` keys and target plugin descriptors breaks target creation at registry/config-manager time.

## Test signals
Tests verify the AMQP descriptor is present, exposes the expected AMQP fields, and can create an AMQP target with `TargetID { id: "primary", name: "amqp" }` and no store for the provided base config.
