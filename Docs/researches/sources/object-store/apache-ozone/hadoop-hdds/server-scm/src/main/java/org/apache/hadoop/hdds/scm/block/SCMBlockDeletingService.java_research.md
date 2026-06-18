# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMBlockDeletingService.java

Purpose: Background SCM service that scans pending deleted-block transactions and enqueues delete-block commands to datanodes.

Important APIs and types: Extends `BackgroundService` and implements `SCMService`. Uses `DeletedBlockLog`, `NodeManager`, `EventPublisher`, `SCMContext`, `SCMServiceManager`, `ScmConfig`, `DeleteBlocksCommand`, and deletion metrics.

Control flow: The scanner runs only when leader-ready, out of safe mode, and past the safe-mode-exit delay. It selects healthy datanodes under command limits, checks commit-map size threshold, gets transactions, emits one `DeleteBlocksCommand` per datanode, records command creation, fires `SCMEvents.DATANODE_COMMAND`, updates metrics, and increments retry counts.

State and persistence behavior: Holds runtime service status, safe-mode exit time, limits, clock, and collaborators. Persistent state remains in `DeletedBlockLog`.

Dependencies and integration points: Integrates with SCM lifecycle, leader/safe-mode state, datanode command queues, event publishing, heartbeat delivery, reconfiguration, and metrics.

Risks: Command limits can starve deletion or overload datanodes if misconfigured. Large commit maps pause deletion. Leadership races are mitigated but still important.

Test signals: Verify service gating, datanode filtering, command generation, metrics, retry increments, threshold skipping, and dynamic block deletion limit validation.
