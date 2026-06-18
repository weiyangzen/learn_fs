# sources/object-store/rustfs/crates/notify/src/registry.rs

## Purpose
Manages target plugin registration and target construction from notification configuration.

## Important APIs, types, and functions
- `TargetRegistry` wraps `TargetPluginRegistry<Event>`.
- `new` registers all built-in notify target plugins.
- `supports_target_type` queries plugin support.
- `create_target` creates one target from target type, instance id, and KVS.
- `create_targets_from_config` delegates full config/environment target discovery and creation using `NOTIFY_ROUTE_PREFIX`.

## Control flow
The registry is built at notification system construction time. Config initialization/reload asks it to create all enabled targets concurrently through the underlying plugin registry.

## State and persistence behavior
Registry state is plugin metadata only. Target runtime state is returned to callers and managed by `NotifyRuntimeFacade`/`EventNotifier`.

## Dependencies and integration points
Uses `factory::builtin_target_plugins`, `rustfs_targets::{TargetPluginRegistry, Target, TargetError}`, `rustfs_config::server_config::{Config, KVS}`, and `NOTIFY_ROUTE_PREFIX`. It is the bridge between server config/env target settings and concrete target instances.

## Risks and edge cases
Create behavior depends on plugin registry semantics, including environment override handling and enabled filtering. Unsupported target types fail in the lower registry. Any new notify target must be present in the built-in catalog or registered here.

## Test signals
A unit test confirms the AMQP target type is registered.
