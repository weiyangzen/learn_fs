## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportHandler.java

Purpose: this handler customizes SCM's full container report handling for Recon by ensuring Recon learns any containers missing from its local SCM DB before normal FCR processing runs.

Important APIs and types: it extends `ContainerReportHandler`, overrides `getLogger`, and overrides `onMessage(ContainerReportFromDatanode, EventPublisher)`. It casts `getContainerManager()` to `ReconContainerManager` and uses `ContainerReplicaProto` entries from the full report.

Control flow: on each full report, the handler extracts the report's replica list, calls `ReconContainerManager.checkAndAddNewContainerBatch`, and then invokes `super.onMessage` so SCM's shared report processor can update replicas and lifecycle state. This ordering is important because the parent handler expects containers to exist locally.

State and persistence: the handler owns no durable state. Persistence happens indirectly through `ReconContainerManager`, which writes container entries, pipeline membership, and replica history to Recon's RocksDB-backed managers.

Dependencies and integration points: registered in `ReconStorageContainerManagerFacade` under `SCMEvents.CONTAINER_REPORT` using a fixed thread pool with affinity shared with ICR events. It integrates with `ReconContainerReportQueue`, which can merge adjacent ICRs but preserves FCR ordering.

Risks and edge cases: the unconditional cast requires the facade to supply a `ReconContainerManager`. If SCM verification of missing containers fails, parent processing may still see unknown containers and log or skip according to shared SCM behavior. Large FCRs rely on the batch path in `ReconContainerManager` for scalability.

Test signals: no isolated test was found for this class, but container report behavior is indirectly covered by Recon SCM and container endpoint tests. Useful focused tests would verify "add before super" behavior for unknown containers and that exceptions from the add path do not corrupt later report handling.
