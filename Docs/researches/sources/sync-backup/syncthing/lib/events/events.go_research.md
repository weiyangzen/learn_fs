## sources/sync-backup/syncthing/lib/events/events.go

Purpose: Provides process-wide event logging, subscription, polling, buffering, event type string/JSON handling, and noop logger implementations.

Important APIs/types/functions: `EventType` constants and `AllEvents`; `String`, `MarshalText`, `UnmarshalJSON`, `UnmarshalEventType`; interfaces `Logger`, `Subscription`, `BufferedSubscription`; structs `logger`, `Event`, `subscription`, `bufferedSubscription`; `NewLogger`, `Serve`, `Log`, `sendEvent`, `Subscribe`, `unsubscribe`, `Poll`, `NewBufferedSubscription`, `Since`, `Error`, `NoopLogger`.

Control flow: `Logger.Serve` serializes all event delivery, subscription creation, and unsubscription through channels. `Log` enqueues an event. `sendEvent` assigns global IDs, checks subscription masks, assigns per-subscription IDs, delivers with a 15 ms timeout, and records created/delivered/dropped metrics. `Subscribe` schedules subscription creation on the logger goroutine. `Poll` resets a per-subscription timer and waits for event or timeout. Buffered subscriptions continuously drain an underlying subscription into a ring buffer and `Since` waits until newer subscription IDs are available.

State and persistence: In-memory subscription slices, per-subscription next IDs, global ID counter, event channels, timers, ring buffers, condition variable, and metrics. No durable persistence.

Dependencies and integration points: Used throughout Syncthing for API events; discovery and connection services log `DeviceDiscovered` and `ListenAddressesChanged`. Uses suture service interface, `syncutil.TimeoutCond`, Prometheus metrics.

Risks: `Log` blocks when the logger service is not running and event channel fills. Slow subscribers can drop events after timeout by design. `Poll` is not safe for concurrent calls on the same subscription. Buffered ring buffers overwrite old events, so clients must poll often enough.

Test signals: `events_test.go` covers subscription masks, timeouts, IDs, buffering, JSON unmarshal, unsubscribe behavior, contention, and benchmarks.
