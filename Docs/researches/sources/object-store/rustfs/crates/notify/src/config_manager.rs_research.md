# sources/object-store/rustfs/crates/notify/src/config_manager.rs

## Purpose
Coordinates notification target configuration with the live runtime. It owns the shared server `Config`, constructs configured targets through `TargetRegistry`, activates replay-capable target runtimes through `NotifyRuntimeFacade`, and persists target config mutations back into the object-store backed server config.

## Important APIs, types, and functions
- `NotifyConfigManager` holds `Arc<RwLock<Config>>`, `Arc<TargetRegistry>`, `NotifyRuleEngine`, and `NotifyRuntimeFacade`.
- `init` clones the current config, creates targets, activates them with replay, and replaces the runtime target set.
- `reload_config` updates the in-memory config, rebuilds targets from a supplied `Config`, activates replay, and commits the replacement runtime.
- `set_target_config`, `remove_target`, and `remove_target_config` wrap persistent config mutation through `update_config_and_reload`.
- `runtime_target_id_for_subsystem` maps config subsystem names such as `notify_webhook` to runtime target types such as `webhook`; target names are lowercased.
- `notify_configuration_hint` emits an operator hint for empty notification target configuration.

## Control flow
Initialization and reload both follow the same path: read or accept a `Config`, call `TargetRegistry::create_targets_from_config`, pass the resulting target boxes to `NotifyRuntimeFacade::activate_targets_with_replay`, then call `replace_targets`. Mutating APIs read the persisted server config via `rustfs_ecstore::config::com::read_config_without_migrate`, apply a closure, skip reload if unchanged, save the new config, then reload.

## State and persistence behavior
The authoritative target configuration is persisted with `save_server_config` through the global object-store handle. The manager also updates the shared in-memory `Config` behind an async `RwLock`. Runtime target state is replaced atomically through the runtime facade after config persistence succeeds. `remove_target_config` protects referential integrity by asking `NotifyRuleEngine::is_target_bound_to_any_bucket` before deletion.

## Dependencies and integration points
Integrates `rustfs_config::notify` subsystem constants, `rustfs_ecstore` global storage/config APIs, `rustfs_targets` target creation and `TargetID`, `TargetRegistry`, `NotifyRuleEngine`, and `NotifyRuntimeFacade`. Logging uses structured `tracing` fields for lifecycle and config update events.

## Risks and edge cases
Target removal fails if server storage is not initialized, so API callers must distinguish runtime-only state from persisted config state. The config key path lowercases type/name; callers using mixed-case names must rely on this normalization. Deleting an unbound target is idempotent, but a target bound to any bucket rule is blocked to avoid dangling bucket notifications. Empty target sets are legal and logged with an idle hint.

## Test signals
Tests confirm empty `init` and `reload_config` succeed, and verify subsystem-to-runtime target ID mappings for webhook, AMQP, MQTT, Kafka, NATS, Pulsar, Redis, and Postgres. The persistence paths are not deeply integration-tested here because they require initialized object-store config storage.
