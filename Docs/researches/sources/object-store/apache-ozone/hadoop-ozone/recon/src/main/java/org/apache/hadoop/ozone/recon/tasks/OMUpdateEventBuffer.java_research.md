# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBuffer.java

Purpose: `OMUpdateEventBuffer` is a bounded queue for Recon events while task reprocessing or async delta processing is active. It prevents OM sync from directly blocking on expensive task work and provides overflow signals for full snapshot fallback.

Important APIs and types: `offer(ReconEvent)` enqueues OM update batches or control events, increments `totalBufferedEvents`, updates `ReconTaskControllerMetrics`, and records dropped batches when the queue is full. `poll(long)` blocks up to a timeout, decrements buffered event counts, and increments processed event metrics. `getQueueSize()`, `getDroppedBatches()`, `resetDroppedBatches()`, `clear()`, and `drainTo(Collection)` are used by controller logic and tests.

Control flow and integration: `ReconTaskControllerImpl` owns one buffer. Normal delta events are enqueued by `consumeOMEvents`; `processBufferedEventsAsync` polls and dispatches. Reinitialization events are also enqueued through the same buffer. On overflow, the controller drains events, cleans checkpoint resources, and requests full-snapshot style recovery.

State and persistence: state is in-memory only: a `LinkedBlockingQueue`, total buffered event counter, and dropped batch counter. Metrics mirror queue state but are not authoritative persistence.

Dependencies: `BlockingQueue`, atomics, `ReconEvent`, `ReconTaskControllerMetrics`, SLF4J.

Risks and test signals: `drainTo` subtracts the sum over the entire supplied collection, not only newly drained elements, so callers should pass an empty collection. Overflow tests should verify dropped counters, metric increments, queue size, interrupt handling in `poll`, and counter consistency after drains and clears.
