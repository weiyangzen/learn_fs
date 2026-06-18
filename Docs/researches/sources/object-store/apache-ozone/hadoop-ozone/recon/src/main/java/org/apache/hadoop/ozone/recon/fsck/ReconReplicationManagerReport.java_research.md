## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManagerReport.java

Purpose: Recon extension of SCM `ReplicationManagerReport` that tracks all replica-checksum mismatch containers separately from SCM health states.

Important APIs/types/functions: constructor disables base sample-list allocation with `super(0)`; `addReplicaMismatchContainer`; `getReplicaMismatchContainers` returns an unmodifiable list.

Control flow: regular SCM counters remain in the superclass; Recon-specific `REPLICA_MISMATCH` IDs are accumulated in a separate list and later persisted by `ReconReplicationManager`.

State and persistence: in-memory scan report only; persistence occurs elsewhere. Integration is with `ReconReplicationManager.processAll`.

Risks: the list can grow to all containers with mismatches; unlike base samples it is intentionally unbounded. Tests should verify counters still work, mismatch list immutability, and empty/default report behavior.
