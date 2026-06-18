# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventQueue.java

Purpose: `EventQueue` is HDDS/Ozone's simple asynchronous event bus. It maps `Event` identifiers to one or more `(EventExecutor, EventHandler)` registrations and routes published payloads to the matching handlers.

Important APIs/types/functions: constructors optionally accept a thread-name prefix. `addHandler(event, handler)` creates a `SingleThreadExecutor`; `addHandler(event, executor, handler)` installs a caller-provided executor after validating its name. `fireEvent()` publishes payloads. `processAll(timeout)` is a testing-only drain helper. `close()` stops the queue and closes all distinct executors. `setSilent()` suppresses warnings for unhandled events. `getExecutorName()` derives executor names from event and handler names.

Control flow: handlers are stored in `Map<Event, Map<EventExecutor, List<EventHandler>>>`. On publication, the queue increments event counters, finds the executor map for the event, logs payload details at trace/debug levels, and invokes `executor.onMessage(handler, payload, this)` for each handler. `processAll()` repeatedly inspects each executor's queued/successful/failed counters until all executors appear idle or timeout expires.

State and persistence: state is fully in-memory and guarded only by coarse lifecycle flags; registration and publication are not backed by durable storage. `isRunning` prevents new registrations and publications after `close()`.

Dependencies/integration: depends on Jackson for trace serialization, protobuf support for `Message`, Hadoop `Time`, Guava preconditions, and SCM network classes for a mixin that avoids circular `DatanodeDetails` parent serialization. It is the common publisher used by SCM, Recon, safe mode rules, node/container/pipeline handlers, and tests.

Risks: raw collection usage weakens type safety at dispatch. `payload.getClass()` is used for debug logging, so a null payload can fail when debug is enabled. Executor names are strict; custom executors must match `EventQueue.getExecutorName(event, handler)`. The testing drain method is eventually consistent and not safe for production synchronization.

Test signals: `TestEventQueue` covers handler registration, fixed-pool executor dispatch, metrics, and queue processing. `TestEventQueueChain` covers handler-emitted follow-on events. Many SCM/Recon integration tests call `processAll()` to drain event side effects.
