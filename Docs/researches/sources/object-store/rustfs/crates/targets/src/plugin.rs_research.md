# sources/object-store/rustfs/crates/targets/src/plugin.rs

## Purpose
Plugin registry and descriptor layer for constructing target instances from configuration. It packages create/validate callbacks with manifest metadata and provides runtime activation through a `PluginRuntimeAdapter`.

## Important APIs, types, and functions
- `TargetRequestValidator` enumerates admin validation modes for builtin target families.
- `TargetAdminMetadata` and `BuiltinTargetAdminDescriptor` expose subsystem, valid fields, manifest, and validation metadata for admin/control-plane use.
- `TargetPluginDescriptor<E>` owns manifest, target type, valid fields, a config validator closure, and a target factory closure.
- `BuiltinTargetDescriptor<E>` couples plugin descriptors to admin metadata.
- `TargetPluginRegistry<E>` registers descriptors, creates targets, creates all enabled targets from config, and creates runtime activations via an adapter.
- `boxed_target` erases concrete targets into boxed trait objects.

## Control flow
Descriptors validate config before invoking their create callback. Registry config creation iterates registered target types, collects enabled merged configs for each type using `collect_target_configs`, attempts target creation per instance, logs failures, and continues building the rest. `create_activation_from_config` delegates successful targets to a runtime adapter, which may start replay workers.

## State and persistence behavior
Registry state is an in-memory map from target type to descriptor. It does not persist configs or targets. Created targets may own durable queue stores, but that state belongs to target implementations and runtime activation.

## Dependencies and integration points
The module integrates config loading, target trait objects, manifests, runtime adapters, serde bounds for event payloads, and tracing. It is the central connection between legacy config sections and runtime target management.

## Risks and edge cases
Duplicate registration replaces the prior descriptor for a target type. `create_targets_from_config` logs per-target creation errors and returns `Ok` with partial success, so callers must inspect resulting activation if they need all-or-nothing semantics. Registry iteration order comes from `hashbrown::HashMap`, so creation order is not stable.

## Test signals
The unit test registers a synthetic target, materializes one enabled config instance, activates through `BuiltinPluginRuntimeAdapter`, and asserts the expected `primary:test` target appears without replay workers.
