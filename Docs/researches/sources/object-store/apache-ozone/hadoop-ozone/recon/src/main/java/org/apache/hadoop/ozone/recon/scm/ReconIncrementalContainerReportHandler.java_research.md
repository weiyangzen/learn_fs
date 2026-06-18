## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconIncrementalContainerReportHandler.java

Purpose: Recon's ICR handler ensures newly reported containers are known locally before SCM's incremental report logic processes replica updates.

Important APIs and types: extends `IncrementalContainerReportHandler`, overrides `getLogger`, and overrides `onMessage(IncrementalContainerReportFromDatanode, EventPublisher)`. Uses inherited `getDatanodeDetails` and `processICR`.

Control flow: `onMessage` resolves the reporting datanode; if missing, it returns. It then calls `ReconContainerManager.checkAndAddNewContainerBatch` on ICR replicas. On success, it delegates to `processICR` with the resolved datanode; on exception, it logs and returns without applying the ICR.

State and persistence: no owned state. Container additions, lifecycle updates, and replica history are persisted through `ReconContainerManager` and inherited SCM processing.

Dependencies and integration points: registered by the facade under `SCMEvents.INCREMENTAL_CONTAINER_REPORT` using the same affinity executor pool as FCR handling, so FCR-first ordering by datanode can be maintained by the dispatcher/executor setup.

Risks and edge cases: unlike the FCR handler, an exception during pre-add aborts the whole ICR. This avoids parent processing unknown containers but can drop valid replica changes in the same ICR. The cast to `ReconContainerManager` assumes facade wiring.

Test signals: indirect integration tests cover SCM container sync; a focused ICR test should cover unknown container backfill, null datanode early return, and error behavior when SCM verification fails.
