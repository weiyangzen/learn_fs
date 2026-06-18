# sources/object-store/rustfs/crates/notify/src/pipeline.rs

## Purpose
Provides the event pipeline between object operations, live in-process listeners, recent-event history, and external target dispatch.

## Important APIs, types, and functions
- `LiveEventHistory` stores a bounded `VecDeque<(sequence, Arc<Event>)>` and the next sequence number.
- `record` appends an event and evicts older entries over `MAX_RECENT_LIVE_EVENTS` (1024).
- `snapshot_since(after_sequence, limit)` returns a `LiveEventBatch`.
- `NotifyPipeline` owns an `EventNotifier`, a broadcast sender, and shared live history.
- `has_live_listeners`, `subscribe_live_events`, `recent_live_events_since`, and `send_event` are the public pipeline API.
- `NotifyEventBridge` aliases `NotifyPipeline`.

## Control flow
`send_event` records the event under the live history write lock, sends it to the broadcast channel ignoring send errors, then awaits notifier dispatch. Recent-event reads take a read lock and return events with sequence greater than the supplied cursor up to the limit.

## State and persistence behavior
History is in-memory, bounded, and sequence-numbered. Broadcast subscribers are in-process only. Durable queueing, if any, is implemented by target stores after notifier dispatch.

## Dependencies and integration points
Connects `NotificationSystem::send_event`, live listener APIs, and `EventNotifier::send`. Uses `tokio::sync::{broadcast, RwLock}`.

## Risks and edge cases
Broadcast send errors are ignored, which is appropriate when there are no receivers but hides lagged/closed channel details. `snapshot_since` reports truncation when the requested limit is reached, not necessarily when older events have already been evicted; clients must use `next_sequence` defensively. `recent_live_events_since` coerces limit to at least one.

## Test signals
Tests confirm listener count transitions and that sent events are recorded in recent history with expected sequence and object key.
