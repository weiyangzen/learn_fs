# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMUpdateEventBatch.java

Purpose: `OMUpdateEventBatch` is the `ReconEvent` wrapper for a batch of OM DB delta events consumed by Recon tasks. It binds a `List<OMDBUpdateEvent>` to the batch sequence number that downstream task status records use as the last processed OM sequence.

Important APIs and types: the constructor accepts the event list and `batchSequenceNumber`; `getLastSequenceNumber()` exposes the sequence internally to the task package; `getIterator()`, `getEvents()`, and `isEmpty()` expose the batch contents; `getEventType()` returns `OM_UPDATE_BATCH`; `getEventCount()` returns `events.size()` for metrics and buffer accounting.

Control flow and integration: `ReconTaskControllerImpl.consumeOMEvents` offers instances to `OMUpdateEventBuffer`; the async event processor dispatches the batch to registered `ReconOmTask.process` implementations. `OmTableInsightTask.process` iterates through this wrapper.

State and persistence: the class is immutable in fields but does not defensively copy the provided list, so outside mutation of the list would affect later consumers. It does not persist data itself; persistence happens through task status updaters and task-specific managers after processing.

Dependencies: Java collection iterators, `OMDBUpdateEvent`, and the local `ReconEvent` interface.

Risks and test signals: tests should cover empty batches, event count metrics, sequence propagation, and mutation assumptions around the input list. The package-private sequence getter means only same-package controller code can update status from it.
