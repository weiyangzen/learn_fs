## sources/sync-backup/syncthing/lib/events/events_test.go

Purpose: Tests event logger lifecycle, delivery semantics, buffering, IDs, JSON unmarshalling, and unsubscribe contention.

Important APIs/types/functions: `setupLogger`; tests `TestNewLogger`, `TestSubscriber`, `TestTimeout`, `TestEventBeforeSubscribe`, `TestEventAfterSubscribe`, `TestEventAfterSubscribeIgnoreMask`, `TestBufferOverflow`, `TestUnsubscribe`, `TestGlobalIDs`, `TestSubscriptionIDs`, `TestBufferedSub`, `TestSinceUsesSubscriptionId`, `TestUnmarshalEvent`, `TestUnsubscribeContention`; benchmarks `BenchmarkBufferedSub`, `BenchmarkLogEvent`.

Control flow: Tests run a logger service under context, create subscriptions, log events, poll or read channels, and assert event type/data/ID/error behavior. Contention test runs many listener and sender goroutines, then ensures listener unsubscribe completes in reasonable time.

State and persistence: In-memory logger/subscriptions only. `runningTests` is set to stabilize timer branches.

Dependencies and integration points: Exercises Prometheus metric side effects implicitly but does not assert metrics.

Risks: Timing-sensitive tests use one-second/minute thresholds and may be affected by heavily loaded CI, though stabilization hooks reduce flakiness.

Test signals: Strong direct coverage of public event bus behavior and concurrency stress.
