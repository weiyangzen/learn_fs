# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMUpdateEventBuffer.java

Purpose: Unit tests for `OMUpdateEventBuffer`, the bounded queue that buffers ordinary OM update batches and synthetic Recon reinitialization events.

Important APIs and control flow: Tests instantiate a capacity-100 buffer, offer and poll `OMUpdateEventBatch`, fill capacity to assert overflow rejection, poll an empty queue with timeout, enqueue a `ReconTaskReInitializationEvent`, clear the queue, reset dropped-batch counters, and verify `clear` preserves the dropped counter.

State and persistence behavior: State is in-memory queue size and a dropped-batches counter. Overflow increments the counter and returns `false`; `clear` drains pending events but intentionally does not reset overflow evidence. `resetDroppedBatches` explicitly clears the counter.

Dependencies and integration points: Uses `ReconEvent`, `OMUpdateEventBatch`, `OMDBUpdateEvent`, and `ReconTaskReInitializationEvent` with a mocked checkpointed `ReconOMMetadataManager`. This buffer feeds `ReconTaskControllerImpl` async processing and overflow-driven rebuild logic.

Risks and test signals: Good signal for bounded-buffer behavior and event polymorphism. It does not exercise concurrent producer/consumer races or controller-level overflow transitions, which are covered elsewhere.
