# sources/object-store/rustfs/crates/notify/src/notifier.rs

## Purpose
Implements event dispatch to configured runtime targets after bucket rule matching. It also owns the shared runtime target list and send-concurrency limiter.

## Important APIs, types, and functions
- `EventNotifier` holds `NotificationMetrics`, `NotifyRuleEngine`, `SharedNotifyTargetList`, and a send `Semaphore`.
- `send` matches target IDs, skips missing/disabled targets, spawns per-target save tasks, and waits for them.
- `get_arn_list`, `remove_all_bucket_targets`, `target_list`, and `init_bucket_targets_shared` expose runtime target list operations.
- `TargetList` wraps `TargetRuntimeManager<Event>` and supports add/get/keys/values, close-aware removal/clear, runtime metrics, health snapshots, status snapshots, and mutable runtime access for `NotifyRuntimeFacade`.

## Control flow
`send` extracts bucket, object key, and event name from an `Event`, asks the rule engine for matching targets, increments skipped metrics if none match, then reads the target list. For each matching runtime target it skips disabled targets, builds an `EntityTarget<Event>`, spawns a task gated by the send semaphore, calls `target.save`, and updates metrics based on success/failure and whether the target has a deferred store. Missing runtime targets are logged and counted as skipped. The function awaits all spawned tasks before returning.

## State and persistence behavior
The target list is in-memory runtime state. Targets may persist events internally through their `store()` implementation; the notifier only calls `save`. Metrics are updated around task execution. `remove_all_bucket_targets` and close-aware target-list methods call target close paths through the target runtime manager.

## Dependencies and integration points
Uses `rustfs_targets::{Target, EntityTarget, TargetRuntimeManager, SharedTarget}`, `TargetID`, `NotifyRuleEngine`, `NotificationMetrics`, `tokio::spawn`, and `tokio::sync::{RwLock, Semaphore}`. Send concurrency is configured by `ENV_NOTIFY_SEND_CONCURRENCY` with a default from `rustfs_config`.

## Risks and edge cases
Disabled targets are skipped without incrementing the skipped counter in the per-target branch. Metrics for deferred targets decrement processing rather than incrementing processed because final delivery comes from replay/queue processing. Because `send` waits for all target tasks, slow direct targets affect caller latency up to target `save` duration. Missing runtime targets can occur when bucket rules reference targets not currently active.

## Test signals
Tests verify encoded key matching behavior through the rule engine, disabled targets are not called, and prefix/suffix filters dispatch only matching objects. Test targets implement the target trait and count save calls.
