# sources/object-store/rustfs/crates/ecstore/src/event/targetlist.rs

Purpose: This file defines the runtime counter shell for notification targets. It is currently a partial implementation: counters exist, while concrete target storage, queues, and target stats are commented out.

Important APIs and types: `TargetList` has public atomic counters `current_send_calls`, `total_events`, `events_skipped`, and `events_errors_total`, all `AtomicI64`. `TargetList::new` returns the default value. Private unused structs `TargetStat` and `TargetIDResult` sketch per-target counters and target-result error reporting.

Control flow: There is no send, add, remove, or queueing logic here. The only active flow is constructing zeroed atomics via `Default`.

State and persistence behavior: The counters are process-local atomics, intended for concurrent notification metrics. They are not persisted and are currently only read by `EventNotifier::get_arn_list` for a warning log count. No code in this file increments them.

Dependencies and integration points: `EventNotifier` embeds a `TargetList`. The file imports `TargetID` for the private result struct and has comments for a future `HashMap<TargetID, Target>`, async event queue, and `HashMap<TargetID, TargetStat>`.

Risks: The public counters can be modified by external code if the `TargetList` is visible, but there is no API-level invariant tying them to actual dispatch. Because target storage is commented out, reporting based on these counters can imply notification support that does not exist. The private stat/result structs are unused and may drift from any eventual target implementation.

Test signals: There are no local tests. The only indirect signal is `event_notification` construction and dispatch-hook tests, which do not touch target counters.
