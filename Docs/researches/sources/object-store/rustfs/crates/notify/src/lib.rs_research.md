# sources/object-store/rustfs/crates/notify/src/lib.rs

## Purpose
Crate root for RustFS notification support. It declares internal modules and re-exports the public API for notification events, global lifecycle, runtime management, rule configuration, targets, metrics, and status views.

## Important APIs, types, and functions
- Internal modules include config, event, global, pipeline, rule engine, runtime facade/view, services, status, bucket config manager, and subscriber view.
- Public modules: `factory`, `integration`, `notifier`, `registry`, and `rules`.
- Re-exports include `NotificationSystem`, `NotificationError`, `Event`, `EventArgs`, `EventArgsBuilder`, `NotifyConfigManager`, `NotifyRuleEngine`, `NotifyRuntimeFacade`, `NotifyRuntimeView`, `NotifyServices`, and global functions.

## Control flow
No executable control flow beyond module resolution and public exports.

## State and persistence behavior
No local state. Publicly exposes stateful components implemented in other modules, including the process-global notification system from `global.rs`.

## Dependencies and integration points
This root module defines the public surface consumed by RustFS server code and other crates. It also keeps several implementation modules private while exposing selected types.

## Risks and edge cases
Changing module visibility or re-exports is a public API change. `bucket_config_manager` is private as a module but `NotifyBucketConfigManager` is re-exported, so internals remain hidden while the type stays accessible.

## Test signals
No direct tests. Compilation of downstream tests validates the re-export surface.
