# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcherMetrics.java

Purpose: `EventWatcherMetrics` is the metrics bean registered by `EventWatcher`. It records how many events are tracked, completed, timed out, and the completion-time rate distribution.

Important APIs/types/functions: `incrementTrackedEvents()`, `incrementTimedOutEvents()`, `incrementCompletedEvents()`, and `updateFinishingTime(duration)` mutate `MutableCounterLong` and `MutableRate` fields. Package-private getters expose metric objects to tests.

Control flow: `EventWatcher.start()` registers this object with the default Metrics2 system. `EventWatcher` updates counters in start, completion, and timeout paths.

State and persistence: state is in memory inside Metrics2 mutable metric objects. There is no explicit unregister method in this class; lifecycle is managed by the registering watcher and metrics system.

Dependencies/integration: depends on Hadoop Metrics2 annotations and mutable metric types. Integrated only through `EventWatcher`.

Risks: fields rely on Metrics2 injection after registration. Instantiating and using the class outside Metrics2 registration may leave fields null. Reusing names across watchers can create metrics-source conflicts at registration time.

Test signals: `TestEventWatcher` obtains metrics via a visible-for-testing watcher accessor and asserts counter/rate behavior after timeout and completion scenarios.
