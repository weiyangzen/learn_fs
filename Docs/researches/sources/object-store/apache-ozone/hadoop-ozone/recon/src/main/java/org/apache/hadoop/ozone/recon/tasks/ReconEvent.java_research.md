# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconEvent.java

Purpose: `ReconEvent` is the small envelope interface that lets `OMUpdateEventBuffer` carry both OM delta batches and Recon control events.

Important APIs and types: implementors expose `getEventType()` and `getEventCount()`. `EventType` currently has `OM_UPDATE_BATCH` and `TASK_REINITIALIZATION`.

Control flow and integration: `OMUpdateEventBatch` returns `OM_UPDATE_BATCH`; `ReconTaskReInitializationEvent` returns `TASK_REINITIALIZATION`. `ReconTaskControllerImpl.processReconEvent` switches on the type to call either delta processing or task reinitialization.

State and persistence: no state or persistence. The event count is used for queue accounting and metrics.

Dependencies: none outside the package.

Risks and test signals: adding a new event type requires controller dispatch support and metrics semantics for event counts. Tests should cover dispatch behavior for all enum values and unknown/default paths if the enum expands.
