<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java

Purpose: tests `EventWatcher` lease-based tracking, completion filtering, timeout emission, in-progress queries, and watcher metrics.

Important APIs/types/functions: `EventWatcher`, `EventWatcherMetrics`, `LeaseManager`, `IdentifiableEventPayload`, `TypedEvent`, `EventQueue`, `EventHandlerStub`, `getTimeoutEvents`, `contains`, `getMetrics`, `onTimeout`, `onFinished`, and `HddsIdFactory`.

Control flow: setup starts a `LeaseManager`, teardown shuts it down. A concrete `CommandWatcherExample` listens for under-replicated start events and completion events. Tests fire watch events, optionally fire completion events, sleep/process until leases expire, then assert timed-out payloads were republished to `UNDER_REPLICATED`. Additional tests query in-progress events by predicate and inspect metrics after one completed and two timed-out events.

State and persistence behavior: state lives in the lease manager, watcher tracking map, metrics counters/gauges, and test helper event lists. No disk state.

Dependencies and integration points: integrates event queue dispatch with lease expiration and metrics. Test payloads implement identity-based equality/hash code to allow correlation between start and completion events.

Risks: sleep/lease-timeout tests are timing-sensitive and may need generous timeouts under load. Metrics assertions depend on exact accounting semantics for tracked/completed/timed-out events.

Test signals: asserts no premature timeout emission, completed events suppress timeout, only unfinished events are republished, in-progress filter results, `contains` transitions, tracked/completed/timed-out metric relationships, and positive timeout counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java -->
