# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskReInitializationEvent.java

Purpose: `ReconTaskReInitializationEvent` is the control event used to request asynchronous full reinitialization of Recon OM tasks from a checkpointed OM metadata manager.

Important APIs and types: `ReInitializationReason` includes `BUFFER_OVERFLOW`, `TASK_FAILURES`, and `MANUAL_TRIGGER`. The constructor stores reason, current timestamp, and `ReconOMMetadataManager` checkpoint. Getters expose those values; `getEventType` returns `TASK_REINITIALIZATION`; `getEventCount` returns 1.

Control flow and integration: `ReconTaskControllerImpl.queueReInitializationEvent` creates this event after successful checkpoint creation and offers it to `OMUpdateEventBuffer`. The async processor calls `processReInitializationEvent`, which uses the checkpointed manager in try-with-resources and cleans checkpoint files afterward.

State and persistence: the event holds an in-memory reference to a checkpointed metadata manager backed by temporary checkpoint files. It does not write status itself.

Dependencies: `ReconOMMetadataManager`, `ReconEvent`.

Risks and test signals: because it owns resource-like state, discarded or drained events must close and clean their checkpoint managers. Tests should cover event type/count, timestamp creation, reason propagation, and cleanup paths when queued events are drained before processing.
