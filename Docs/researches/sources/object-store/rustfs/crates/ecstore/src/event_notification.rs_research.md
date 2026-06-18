# sources/object-store/rustfs/crates/ecstore/src/event_notification.rs

Purpose: This file provides the ecstore event notification facade. The full notifier methods are mostly no-op stubs that log warnings, while the active dispatch path is a global one-shot hook used by `send_event`.

Important APIs and types: `EventNotifier::new` returns `Arc<RwLock<EventNotifier>>` with an embedded `TargetList`. Private methods `get_arn_list`, `set`, `init_bucket_targets`, and `send` currently log not-implemented warnings and either return empty values or `Ok(())`. `EventArgs` carries `event_name`, `bucket_name`, `ObjectInfo`, request parameters, response elements, host, and user agent. `EventDispatchHook` is `Arc<dyn Fn(EventArgs) + Send + Sync + 'static>`, stored in `EVENT_DISPATCH_HOOK: OnceLock<_>`. Public functions `register_event_dispatch_hook` and `send_event` are the active API.

Control flow: Callers construct `EventArgs` at object, lifecycle, replication, and restore points and call `send_event`. If a hook has been registered, `send_event` invokes it synchronously and returns. If no hook exists, the event is dropped after a warning. `register_event_dispatch_hook` succeeds only once because `OnceLock::set` rejects subsequent hooks. The `EventNotifier` instance in global/store state is not used by `send_event`.

State and persistence behavior: The only active mutable state is the process-global hook. It is not resettable, which affects test isolation and embedding. `EventArgs` is transient and no events are persisted or queued. `TargetList` counters are present but not incremented by `send_event`.

Dependencies and integration points: `global.rs` creates `GLOBAL_EventNotifier`, and `store/init.rs` passes it into `ECStore`. `set_disk.rs`, lifecycle operations, and replication resyncer call `send_event` for object restore, lifecycle deletion, tiering, and replication notifications. `EventArgs` depends on `ObjectInfo`; notifier stubs reference `BucketMetadata` and `ECStore`.

Risks: In the default build, events are dropped unless an external hook is registered before use. The hook is one-shot and cannot be unregistered or replaced, which can make tests order-dependent and makes runtime reconfiguration difficult. Synchronous hook execution means a slow or panicking hook directly affects the caller. The private no-op `EventNotifier` methods can mislead integration code expecting bucket rules or target ARNs to work.

Test signals: A unit test registers a hook that increments an atomic counter and verifies `send_event` dispatches once. It deliberately tolerates the one-shot global by ignoring registration failure and comparing the counter before and after the send.
