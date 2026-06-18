# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcher.java

Purpose: `EventWatcher` tracks started events and invokes timeout or completion callbacks based on a lease. It is designed for retry/resend workflows where an initiating payload should be followed by a completion payload before a timeout.

Important APIs/types/functions: constructor takes a watcher name, start event, completion event, and `LeaseManager<Long>`. `start(EventQueue)` registers internal handlers for both events and registers `EventWatcherMetrics`. `contains()`, `remove()`, and `getTimeoutEvents(predicate)` expose tracked payload state. Subclasses implement `onTimeout()` and `onFinished()`.

Control flow: start-event handling stores the payload by id, tracks start time, and acquires a lease whose callback calls `handleTimeout()`. Completion handling releases the lease, removes the tracked payload, updates completion metrics, and calls `onFinished()`. Timeout handling removes state, increments timeout metrics, and calls `onTimeout()`.

State and persistence: tracked payloads are in `ConcurrentHashMap`, `HashSet`, and `HashMap`; mutation methods are synchronized around the multi-structure invariants. There is no persistence. Identity is the payload's `getId()` from `IdentifiableEventPayload`.

Dependencies/integration: depends on `LeaseManager` and Ozone lease exceptions, `EventQueue`, `EventPublisher`, and Hadoop Metrics2. Subclasses are used where SCM needs to monitor asynchronous operations.

Risks: duplicate start ids do not reset the lease; a repeated start overwrites map/time state but `LeaseAlreadyExistException` is ignored, which can surprise callers expecting timeout extension. `handleTimeout()` removes by id then calls `payload.getId()` indirectly through removal state; a missing payload would risk null handling. Metrics source names must be unique per watcher.

Test signals: `TestEventWatcher` covers timeout firing, completion cancellation, removal, timeout-event filtering, and metrics increments for tracked, completed, timed-out, and completion-time state.
