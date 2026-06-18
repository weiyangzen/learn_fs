# sources/object-store/rustfs/crates/notify/src/services.rs

## Purpose
Aggregates the notification subsystem's service facades into one cloneable struct used by `NotificationSystem`.

## Important APIs, types, and functions
- `NotifyServices` fields: `bucket_config_manager`, `config_manager`, `pipeline`, `runtime_facade`, `runtime_view`, and `status_view`.
- `NotifyServices::new` wires shared dependencies into each facade.

## Control flow
The constructor receives already-created shared dependencies from `NotificationSystem::new`, builds runtime view/facade over the shared target list and replay workers, builds config manager over shared config/registry/rule engine/runtime facade, builds bucket config manager over notifier/rule engine/subscriber view, builds pipeline over notifier/live events, and builds status view over metrics.

## State and persistence behavior
The struct owns cloneable service handles; state is in the shared Arcs passed in. Persistence remains in config manager, and runtime state remains in target list/replay workers.

## Dependencies and integration points
It is the composition layer between `NotificationSystem` and lower services. Depends on notification metrics, registry, rule engine, target list, replay workers, broadcast channel, live history, and subscriber view.

## Risks and edge cases
The constructor has many arguments, so dependency ordering mistakes are possible; clippy's too-many-arguments lint is explicitly allowed. All services sharing the same `NotifyRuleEngine` clone is critical for dispatch/subscriber consistency.

## Test signals
A unit test builds services with empty dependencies and asserts the runtime view is empty and status metrics start at zero.
