# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventHandler.java

Purpose: `EventHandler<PAYLOAD>` is the functional callback contract for consumers of `EventQueue` events. It lets event processors react to a typed payload and optionally publish follow-on events through the supplied `EventPublisher`.

Important APIs/types/functions: the sole method is `onMessage(PAYLOAD payload, EventPublisher publisher)`. The interface is annotated with `@FunctionalInterface`, so handlers can be lambdas, method references, or concrete classes.

Control flow: `EventQueue.fireEvent()` finds registered handlers and passes each handler to an `EventExecutor`. The executor controls threading and calls `onMessage`; handlers can invoke `publisher.fireEvent()` to build event chains.

State and persistence: the interface stores no state. Implementations may hold component state, and their thread-safety expectations depend on the executor. The Javadoc says event executors should guarantee a handler implementation is called from one thread, but custom executors must preserve that expectation themselves.

Dependencies/integration: implemented broadly across SCM, Recon, container, and safe-mode code paths. Integrates with `EventPublisher`, `EventExecutor`, `SingleThreadExecutor`, and `FixedThreadPoolWithAffinityExecutor`.

Risks: handler exceptions are caught and counted by executor implementations, but caller-visible failure propagation is intentionally absent. Handlers that publish recursive events can create long asynchronous chains, so tests use `EventQueue.processAll()` to drain them.

Test signals: `TestEventQueue`, `TestEventQueueChain`, and many SCM/Recon tests register lambdas or handler classes and verify asynchronous dispatch, chained events, and executor isolation.
